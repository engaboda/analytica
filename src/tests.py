import io
import unittest

from .app import app
from .models import FileInfo


class BaseTest(unittest.TestCase):
    def setUp(self) -> None:
        app.testing = True
        self.client = app.test_client()


class UploadFileApiTestCase(BaseTest):
    def setUp(self) -> None:
        super().setUp()
        self.upload_tabular_url = "/api/tabular"

    def test_upload_csv_file(self):
        file = io.BytesIO()
        file.write(b"Age,Sex,Name\n28,male,Aboda")
        file.seek(0)
        response = self.client.post(
            self.upload_tabular_url,
            data={"tabular_file": (file, "test.csv")},
            content_type='multipart/form-data'
        )
        file = FileInfo.objects(id=response.json.get('id')).first()
        self.assertIsNotNone(file)
        self.assertEquals(file.file_type, 'csv')

    def test_list_files(self):
        file = io.BytesIO()
        file.write(b"Age,Sex,Name\n28,male,Aboda")
        file.seek(0)
        FileInfo.objects.create(
            file=file, file_type='csv'
        )
        response = self.client.get(
            self.upload_tabular_url
        )
        self.assertTrue(len(response.json) >= 1)


class TabularHeadApiTestCase(BaseTest):

    def setUp(self) -> None:
        super().setUp()
        file = io.BytesIO()
        file.write(b"Age,Sex,Name\n28,male,Aboda")
        file.seek(0)
        file_object = FileInfo.objects.create(
            file=file, file_type='csv'
        )

        self.get_head_url = f"/api/tabular/{file_object.id}/head"

    def test_get_head_of_tabular_file(self):
        response = self.client.get(self.get_head_url)
        self.assertEquals(
            response.json['Age'], [28]
        )
        self.assertEquals(
            response.json['Sex'], ["male"]
        )
        self.assertEquals(
            response.json['Name'], ["Aboda"]
        )


class TabularSelectTestCase(BaseTest):
    def setUp(self) -> None:
        super().setUp()
        file = io.BytesIO()
        file.write(b"Age,Sex,Name\n28,male,Aboda\n10,female,mona\n50,male,John\n30,male,Lufy")
        file.seek(0)
        file_object = FileInfo.objects.create(
            file=file, file_type='csv'
        )

        self.select_column_url = f"/api/tabular/{file_object.id}/select/Age"

    def test_select_column(self):
        response = self.client.get(self.select_column_url)
        self.assertEquals(
            response.json['Age'], {'0': 28, '1': 10, '2': 50, '3': 30}
        )


class TabularSelectWithQueryTestCase(BaseTest):
    def setUp(self) -> None:
        super().setUp()
        file = io.BytesIO()
        file.write(b"Age,Sex,Name\n28,male,Aboda\n10,female,mona\n50,male,John\n30,male,Lufy")
        file.seek(0)
        file_object = FileInfo.objects.create(
            file=file, file_type='csv'
        )

        self.select_column_url_with_query = f"/api/tabular/{file_object.id}/select/Age/</28"

    def test_select_column_with_query(self):
        response = self.client.get(self.select_column_url_with_query)
        self.assertEquals(
            response.json['Age'], {'1': 10}
        )


class TabularSelectWithComplexQueryTestCase(BaseTest):
    def setUp(self) -> None:
        super().setUp()
        file = io.BytesIO()
        file.write(b"Age,Sex,Name\n28,male,Aboda\n10,female,mona\n50,male,John\n30,male,Lufy")
        file.seek(0)
        file_object = FileInfo.objects.create(
            file=file, file_type='csv'
        )

        self.select_column_url_with_complex_query = f'/api/tabular/{file_object.id}/select/Age/>/10/and/Name/==/Aboda'

    def test_select_column_with_complex_query(self):
        response = self.client.get(self.select_column_url_with_complex_query)
        self.assertEquals(
            response.json['Age'], {'0': 28}
        )


class TabularMeanApiTestCase(BaseTest):
    def setUp(self) -> None:
        super().setUp()
        file = io.BytesIO()
        file.write(b"Age,Sex,Name\n28,male,Aboda\n10,female,mona\n50,male,John\n30,male,Lufy")
        file.seek(0)
        file_object = FileInfo.objects.create(
            file=file, file_type='csv'
        )

        self.select_age_and_calculate_mean = f'/api/tabular/{file_object.id}/Age/mean'

    def test_get_mean_for_column_age(self):
        response = self.client.get(self.select_age_and_calculate_mean)
        self.assertEquals(
            response.json['result'],  29.5
        )
