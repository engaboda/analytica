import io
import logging
import os

import PIL
from flask import request
from flask_restful import Resource, fields, marshal_with
from werkzeug import exceptions

from src.models import FileInfo
from src.serializers import TabularDataUploadSerializer, ImageResizerApiSerializer
from src.utils.tabular import TabularHelper
from rake_nltk import Rake

from src.utils.text import ElasticHelper
from PIL import Image
from flask_mongoengine import Pagination
import elasticsearch

logger = logging.getLogger(__name__)


class TabularApi(Resource):
    create_response = {
        "message": fields.String,
        "id": fields.String
    }
    list_response = {
        "data": fields.List(fields.Raw(
            fields.String
        )),
        "next": fields.Boolean,
        "prev": fields.Boolean,
        "count": fields.Integer
    }

    @marshal_with(create_response)
    def post(self):
        tabular_file = request.files.get("tabular_file")
        file_content = tabular_file.stream.read()
        serializer = TabularDataUploadSerializer({
            "tabular_file": tabular_file.filename if tabular_file else '',
        })
        serializer.is_valid()
        _, extension = os.path.splitext(tabular_file.filename)

        file = FileInfo.objects.create(
            file=file_content,
            file_type=extension.replace('.', '')
        )

        return {
            "message": "File Uploaded.",
            "id": file.id
        }

    @marshal_with(list_response)
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('page_size', 10))
        file_type = request.args.get("filter", None)
        filter_kw = {"file_type": file_type} if file_type else {}
        queryset = FileInfo.objects(**filter_kw).order_by('-id')
        result = Pagination(
            queryset, page=page, per_page=per_page
        )
        response = {
            "data": [
                {"_id": str(file.id), "create_at": str(file.create_at), "file_type": file.file_type}
                for file in result.items
            ],
            "next": result.has_next,
            "prev": result.has_prev,
            "count": queryset.count()
        }
        return response


class TabularDeleteApi(Resource):

    def delete(self, pk):
        FileInfo.objects(id=pk).delete()
        return {
            "message": f"file with id: {pk} deleted.",
            "status": "success"
        }

    details_response = {
        "file": fields.String,
        "_id": fields.String,
        "create_at": fields.DateTime,
        "file_type": fields.String
    }

    @marshal_with(details_response)
    def get(self, pk):
        file_info = FileInfo.objects(id=pk).first()
        if not file_info:
            raise exceptions.NotFound("File Not Found.")
        return dict(file_info.to_mongo())


class TabularHead(Resource):

    @staticmethod
    def get(pk):
        file_info = FileInfo.objects(pk=pk).first()
        helper = TabularHelper(file_info.file, file_info.file_type)
        df = helper.read()
        return helper.head(df)


class TabularInfo(Resource):

    tabular_info_response = {
        "info": fields.Raw
    }

    @staticmethod
    @marshal_with(tabular_info_response)
    def get(pk):
        file_info = FileInfo.objects(pk=pk).first()
        helper = TabularHelper(file_info.file, file_info.file_type)
        df = helper.read()
        columns_type = helper.columns_type(df)

        return {
            "info": columns_type
        }


class TabularSelect(Resource):

    @staticmethod
    def get(pk, column_name):
        file_info = FileInfo.objects(id=pk).first()
        if not file_info:
            raise exceptions.NotFound("File Not Found.")
        helper = TabularHelper(file_info.file, file_info.file_type)
        df = helper.read()
        accepted_columns = helper.columns(df)
        if column_name not in accepted_columns:
            return {
                "message": "failed",
                "details": f"accepted Columns to be filter with are: [{', '.join(accepted_columns)}]"
            }
        return {column_name: helper.select(df, column_name)}


class TabularSelectWithQuery(Resource):
    OPERATORS = [">", "<", "==", '!=']

    def __validate_operator(self, operator):
        if operator not in self.OPERATORS:
            raise exceptions.BadRequest({
                "message": "failed",
                "operator": f"Not a valid choice available choices are: [{', '.join(self.OPERATORS)}]",
            })

    def get(self, pk, column_name, operator, value):
        self.__validate_operator(operator)
        file_info = FileInfo.objects(id=pk).first()
        if not file_info:
            raise exceptions.NotFound("File Not Found.")
        helper = TabularHelper(file_info.file, file_info.file_type)
        df = helper.read()
        accepted_columns = helper.columns(df)
        if column_name not in accepted_columns:
            return {
                "message": "failed",
                "details": f"accepted Columns to be filter with are: [{', '.join(accepted_columns)}]"
            }
        return helper.select_with_query(df, column_name, operator, value)


class TabularSelectWithComplexQuery(Resource):
    OPERATORS = ["and", "or"]

    def __validate_operator(self, operator):
        if operator not in self.OPERATORS:
            raise exceptions.BadRequest({
                "message": "failed",
                "operator": f"Not a valid choice available choices are: [{', '.join(self.OPERATORS)}]",
            })

    def get(
            self, pk, right_column_name, right_operator, right_value,
            operator,
            left_column_name, left_operator, left_value
    ):
        self.__validate_operator(operator)
        file_info = FileInfo.objects(id=pk).first()
        if not file_info:
            raise exceptions.NotFound("File Not Found.")
        helper = TabularHelper(file_info.file, file_info.file_type)
        df = helper.read()
        accepted_columns = helper.columns(df)
        if right_column_name not in accepted_columns:
            raise exceptions.BadRequest({
                "message": "failed",
                "details": f"accepted Columns to be filter with are: [{', '.join(accepted_columns)}]"
            })
        if left_column_name not in accepted_columns:
            return exceptions.BadRequest({
                "message": "failed",
                "details": f"accepted Columns to be filter with are: [{', '.join(accepted_columns)}]"
            })
        columns_type = helper.columns_type(df)
        right_column_type = columns_type[right_column_name]['type']
        left_column_type = columns_type[left_column_name]['type']
        cast = TabularHelper.TYPES.get(right_column_type)
        right_value = cast(right_value)
        cast = TabularHelper.TYPES.get(left_column_type)
        if cast == str:
            left_value = f"'{left_value}'"
        return helper.select_with_complex_query(
            df, right_column_name, right_operator, right_value, operator,
            left_column_name, left_operator, left_value
        )


class TabularMeanApi(Resource):

    mean_response = {
        "result": fields.Float
    }

    @staticmethod
    @marshal_with(mean_response)
    def get(pk, column_name):
        file_info = FileInfo.objects(id=pk).first()
        if not file_info:
            raise exceptions.NotFound("File Not Found.")
        helper = TabularHelper(file_info.file, file_info.file_type)
        df = helper.read()
        accepted_columns = helper.columns(df)
        if column_name not in accepted_columns:
            raise exceptions.BadRequest({
                "message": "failed",
                "details": f"accepted Columns to be filter with are: [{', '.join(accepted_columns)}]"
            })
        return {
            "result": helper.mean(df, column_name)
        }


class TabularMedianApi(Resource):

    median_response = {
        "result": fields.Float
    }

    @staticmethod
    @marshal_with(median_response)
    def get(pk, column_name):
        file_info = FileInfo.objects(id=pk).first()
        if not file_info:
            raise exceptions.NotFound("File Not Found.")
        helper = TabularHelper(file_info.file, file_info.file_type)
        df = helper.read()
        accepted_columns = helper.columns(df)
        if column_name not in accepted_columns:
            raise exceptions.BadRequest({
                "message": "failed",
                "details": f"accepted Columns to be filter with are: [{', '.join(accepted_columns)}]"
            })
        return {
            "result": helper.median(df, column_name)
        }


class TabularModeApi(Resource):

    median_response = {
        "result": fields.Float
    }

    @staticmethod
    @marshal_with(median_response)
    def get(pk, column_name):
        file_info = FileInfo.objects(id=pk).first()
        if not file_info:
            raise exceptions.NotFound("File Not Found.")
        helper = TabularHelper(file_info.file, file_info.file_type)
        df = helper.read()
        accepted_columns = helper.columns(df)
        if column_name not in accepted_columns:
            raise exceptions.BadRequest({
                "message": "failed",
                "details": f"accepted Columns to be filter with are: [{', '.join(accepted_columns)}]"
            })
        return {
            "result": helper.mode(df, column_name)
        }


class TabularQuantileApi(Resource):

    median_response = {
        "result": fields.Raw
    }

    @staticmethod
    @marshal_with(median_response)
    def get(pk, column_name):
        file_info = FileInfo.objects(id=pk).first()
        if not file_info:
            raise exceptions.NotFound("File Not Found.")
        helper = TabularHelper(file_info.file, file_info.file_type)
        df = helper.read()
        accepted_columns = helper.columns(df)
        if column_name not in accepted_columns:
            raise exceptions.BadRequest({
                "message": "failed",
                "details": f"accepted Columns to be filter with are: [{', '.join(accepted_columns)}]"
            })
        return {
            "result": helper.quantile(df, column_name)
        }


class TabularUpdateDataSetApi(Resource):

    @staticmethod
    def put(pk, index):
        index = int(index)
        file_info = FileInfo.objects(id=pk).first()
        if not file_info:
            raise exceptions.NotFound("File Not Found.")
        helper = TabularHelper(file_info.file, file_info.file_type)
        df = helper.read()
        values = request.json

        for key, value in values.items():
            df.loc[index, key] = value

        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer)
        csv_buffer.seek(0)

        content = csv_buffer.getvalue()
        file_info.file = content
        file_info.save()
        csv_buffer.close()
        return {
            **df.loc[index].to_dict()
        }

    @staticmethod
    def delete(pk, index):
        index = int(index)
        file_info = FileInfo.objects(id=pk).first()
        if not file_info:
            raise exceptions.NotFound("File Not Found.")
        helper = TabularHelper(file_info.file, file_info.file_type)
        df = helper.read()

        try:
            df = df.drop(index=index, axis=1)
        except KeyError:
            raise exceptions.BadRequest({
                "message": "failed",
                "details": f"row not found in dataset."
            })

        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer)
        csv_buffer.seek(0)

        content = csv_buffer.getvalue()
        file_info.file = content
        file_info.save()
        csv_buffer.close()
        return {
            "message": "success",
            "details": f"row: {index} has been deleted."
        }


class TextFullSearch(Resource):

    @staticmethod
    def post():
        data = request.json
        helper = ElasticHelper()
        response = helper.client.search(
            index="classification",
            query={
                "match": {
                    f"{data.get('field')}": {
                        "query": f"{data.get('value')}"
                    }
                }
            }
        )
        return dict(response)


class AllDocumentsApi(Resource):

    @staticmethod
    def get():
        helper = ElasticHelper()
        try:
            response = helper.client.search(
                index="classification",
                body={"query": {"match_all": {}}},
                scroll='2s'
            )
        except elasticsearch.NotFoundError:
            logger.exception("index not found index name: classification")
            return {
                "message": "index not found.",
                "status": "failed"
            }
        except Exception as error:
            logger.exception(f"error: {error}")
            return {
                "message": "unknown error.",
                "status": "failed"
            }
        return dict(response)


class ClassificationApi(Resource):

    @staticmethod
    def post():
        data = request.json
        helper = ElasticHelper()
        response = helper.client.search(
            index="classification",
            **helper.get_mlt_query(data.get('fields'), data.get('like'))
        )
        return dict(response)


class TextKeywordExtraction(Resource):
    """
    Textual information-processing task
        Keyword extraction is a textual information-processing task that automatically identifies and extracts the most
        important words from a document, providing a summary of its content123.
    """

    @staticmethod
    def post():
        data = request.json
        helper = Rake()
        helper.extract_keywords_from_text(data.get("text", ""))
        return helper.get_ranked_phrases()


class UploadImageApi(Resource):
    create_response = {
        "message": fields.String,
        "id": fields.String
    }

    @staticmethod
    @marshal_with(create_response)
    def post():
        image_file = request.files.get("image")
        file_content = image_file.stream.read()

        image = FileInfo.objects.create(
            file=file_content,
            file_type="image"
        )

        return {
            "message": "Image Uploaded",
            "id": image.id
        }


class ImageResizerApi(Resource):
    create_response = {
        "message": fields.String,
        "id": fields.String
    }

    @staticmethod
    @marshal_with(create_response)
    def post(pk):
        image_object = FileInfo.objects(id=pk).first()
        if not image_object:
            raise exceptions.NotFound("File Not Found.")

        serializer = ImageResizerApiSerializer()
        serializer.is_valid()

        size = request.json.get('size')
        image = image_object.file.read()
        try:
            image_with_new_size = Image.frombuffer(mode="RGB", size=tuple(size), data=image, decoder_name="raw")
        except ValueError as error:
            logger.exception(f"Error: {error} while processing image: {pk}")
            raise exceptions.BadRequest({
                "message": "no enough data to resize with requested size.",
                "status": "failed"
            })
        except Exception as error:
            logger.exception(f"Error: {error} while processing image: {pk}")
            raise exceptions.BadRequest({
                "message": "unknown error",
                "status": "failed"
            })
        image_with_new_size_file = io.BytesIO()
        image_with_new_size_file.write(image_with_new_size.tobytes())
        image_with_new_size_file.seek(0)
        image_object.file = image_with_new_size_file.getvalue()
        image_object.save()
        image_with_new_size_file.close()

        return {
            "message": "Image Resized",
            "id": image_object.id
        }


class ImageCropApi(Resource):
    create_response = {
        "message": fields.String,
        "id": fields.String
    }

    @staticmethod
    @marshal_with(create_response)
    def post(pk):
        image_object = FileInfo.objects(id=pk).first()
        if not image_object:
            raise exceptions.NotFound("File Not Found.")

        image = image_object.file.read()
        try:
            image_as_byte = io.BytesIO(image)
            image_buffer = Image.open(image_as_byte)
        except PIL.UnidentifiedImageError as error:
            logger.exception(error)
            raise exceptions.BadRequest({
                "message": "File is empty.",
                "status": "failed"
            })

        left = request.json.get("left")
        right = request.json.get("right")
        top = request.json.get("top")
        bottom = request.json.get("bottom")

        try:
            crop_image = image_buffer.crop((left, top, right, bottom))
        except ValueError as error:
            logger.exception(f"Error: {error} while processing image: {pk}")
            raise exceptions.BadRequest({
                "message": "no enough data to resize with requested size.",
                "status": "failed"
            })
        except Exception as error:
            logger.exception(f"Error: {error} while processing image: {pk}")
            raise exceptions.BadRequest({
                "message": "unknown error",
                "status": "failed"
            })

        crop_image_bytes = io.BytesIO(crop_image.tobytes())
        crop_image_bytes.seek(0)
        image_object.file = crop_image_bytes.getvalue()
        image_object.save()
        crop_image_bytes.close()

        return {
            "message": "Image Cropped",
            "id": image_object.id
        }
