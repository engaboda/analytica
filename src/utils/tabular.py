import logging
import pandas as pd
from werkzeug import exceptions

logger = logging.getLogger(__name__)


class Operand:

    @staticmethod
    def as_query(column, operator, value):
        return f"{column} {operator} {value}"


class TabularHelper:
    TYPES = {
        "object": str,
        "int64": int,
        "float64": float
    }

    def __init__(self, tabular_file, file_type):
        self.tabular_file = tabular_file
        self.file_type = file_type

    @staticmethod
    def columns(df):
        return df.columns.tolist()

    @staticmethod
    def columns_type(df: pd.DataFrame):
        count = df.shape[0]
        return {key: {"type": str(value), "count": count} for key, value in df.dtypes.to_dict().items()}

    def read(self):
        if self.file_type == "csv":
            try:
                df = pd.read_csv(self.tabular_file)
                try:
                    df = df.drop(["Unnamed: 0"], axis=1)
                except KeyError:
                    logger.exception("after saving it add new column with empty name.")
                return df
            except pd.errors.EmptyDataError as error:
                logger.exception(f"Error while reading file: {self.tabular_file} {error}")
                raise exceptions.InternalServerError("File Not readable.")
        return pd.read_excel(self.tabular_file)

    @staticmethod
    def head(df, num_rows=8):
        return df.head(num_rows).to_dict("list")

    @staticmethod
    def select(df, column_name):
        return df[column_name].to_dict()

    @staticmethod
    def select_with_query(df, column_name, condition, value):
        return df.query(f"{column_name} {condition} {value}").to_dict()

    @staticmethod
    def select_with_complex_query(
            df, right_column_name, right_operator, right_value,
            operator, left_column_name, left_operator, left_value
    ):
        right_hand = Operand.as_query(right_column_name, right_operator, right_value)
        left_hand = Operand.as_query(left_column_name, left_operator, left_value)
        return df.query(f"{right_hand} {operator} {left_hand}").to_dict()

    @staticmethod
    def mean(df: pd.DataFrame, column_name):
        return df[column_name].mean()

    @staticmethod
    def median(df: pd.DataFrame, column_name):
        try:
            return df[column_name].median()
        except TypeError as error:
            logger.exception(f"Error: {error} while doing median for column: {column_name}")
            raise exceptions.BadRequest({
                "message": "median can only be done over numerical fields.",
                "status": "failed"
            })
        except Exception as error:
            logger.exception(f"Error: {error} while doing median for column: {column_name}")
            raise exceptions.BadRequest({
                "message": f"unknown error while doing median over column: {column_name}.",
                "status": "failed"
            })

    @staticmethod
    def mode(df: pd.DataFrame, column_name):
        try:
            return df[column_name].mode()
        except TypeError as error:
            logger.exception(f"Error: {error} while doing median for column: {column_name}")
            raise exceptions.BadRequest({
                "message": "median can only be done over numerical fields.",
                "status": "failed"
            })
        except Exception as error:
            logger.exception(f"Error: {error} while doing median for column: {column_name}")
            raise exceptions.BadRequest({
                "message": f"unknown error while doing median over column: {column_name}.",
                "status": "failed"
            })

    @staticmethod
    def quantile(df: pd.DataFrame, column_name):
        try:
            return df[column_name].quantile([0.25, 0.50, 0.75]).to_dict()
        except TypeError as error:
            logger.exception(f"Error: {error} while doing median for column: {column_name}")
            raise exceptions.BadRequest({
                "message": "median can only be done over numerical fields.",
                "status": "failed"
            })
        except Exception as error:
            logger.exception(f"Error: {error} while doing median for column: {column_name}")
            raise exceptions.BadRequest({
                "message": f"unknown error while doing median over column: {column_name}.",
                "status": "failed"
            })
