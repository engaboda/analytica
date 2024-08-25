import logging
import os
from werkzeug import exceptions
from flask_restful import fields
from flask_restful import reqparse
from flask import request

logger = logging.getLogger(__name__)


class ImageResizerApiSerializer:
    image_resizer_api_serializer = reqparse.RequestParser()
    image_resizer_api_serializer.add_argument(
        "size", type=dict, help='Size field contains 2 values for resizing image.',
        required=True
    )

    @staticmethod
    def validate_size(size):
        size_is_empty = not size
        length_of_size_is_more_than_two = len(size) != 2
        if size_is_empty or length_of_size_is_more_than_two:
            raise exceptions.BadRequest({
                "message": "size should have two values",
                "status": "failed"
            })

    def is_valid(self):
        data = request.json
        for key, value in data.items():
            validators = getattr(self, f"validate_{key}")
            if validators:
                validators(value)


class ImageCropApiSerializer:
    image_crop_api_serializer = reqparse.RequestParser()
    image_crop_api_serializer.add_argument("left", type=int, required=True)
    image_crop_api_serializer.add_argument("right", type=int, required=True)
    image_crop_api_serializer.add_argument("top", type=int, required=True)
    image_crop_api_serializer.add_argument("bottom", type=int, required=True)

    @staticmethod
    def validators(left, field_name):
        if not left:
            raise exceptions.BadRequest({
                "message": f"{field_name} field should have numerical value greater than zero.",
                "status": "failed"
            })

    def validate_right(self, right):
        self.validators(right, "right")

    def validate_left(self, left):
        self.validators(left, "left")

    def validate_top(self, top):
        self.validators(top, "top")

    def validate_bottom(self, bottom):
        self.validators(bottom, "bottom")

    def is_valid(self):
        data = request.json
        for key, value in data.items():
            validators = getattr(self, f"validate_{key}")
            if validators:
                validators(value)


class TabularDataUploadSerializer:
    ACCEPTABLE_FILE_EXTENSION = ('.csv', '.xlsx')
    tabular_file = fields.String()

    fields = {
        "tabular_file": {
            "required": True,
        }
    }

    def __init__(self, request_data):
        self.request_data = request_data

    def is_valid(self):
        errors = []

        for field_name in self.fields:
            validator = getattr(self, f"validate_{field_name}")
            is_required = self.fields.get(field_name).get("required")
            if is_required and not self.request_data.get(field_name):
                errors.append(
                    {
                        field_name: f"{field_name} is required field."
                    }
                )
            data = validator(self.request_data.get(field_name))
            if isinstance(data, dict):
                errors.append(data)

        if errors:
            raise exceptions.BadRequest(errors)

    def validate_tabular_file(self, value):
        _, extension = os.path.splitext(value)
        if extension not in self.ACCEPTABLE_FILE_EXTENSION:
            return {
                "tabular_file": f"acceptable file extension with {''.join(self.ACCEPTABLE_FILE_EXTENSION)}"
            }
