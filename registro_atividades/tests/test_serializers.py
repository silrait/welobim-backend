from django.test import TestCase
from ..models import Company
from ..serializers import CompanySerializer

class CompanySerializerTest(TestCase):
    def test_serialize_python_type(self):
        cp = Company(name='Vivente da fronteira LTDA.')
        slz = CompanySerializer(cp)
        self.assertEqual("{'name': 'Vivente da fronteira LTDA.'}", str(slz.data))

