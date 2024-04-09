import pytest
# from django.test import SimpleTestCase
from django.urls import reverse
# from document.views import *


@pytest.mark.django_db
def test_view(client):
   url = reverse('home')
   response = client.get(url)
   assert response.status_code == 200

# class TestUrls(SimpleTestCase):

#     def test_home_url_resolves(self):
#         url = reverse('home')
#         self.assertEquals(resolve(url).func, HomePage)

#     def test_query_url_resolves(self):
#         url = reverse('query')
#         self.assertEquals(resolve(url).func, query)
    
#     def test_sumdb_url_resolves(self):
#         url = reverse('sumdb')
#         self.assertEquals(resolve(url).func, sumdb)

#     def test_groupdb_url_resolves(self):
#         url = reverse('similarity')
#         self.assertEquals(resolve(url).func, groupdb)

#     def test_upload_url_resolves(self):
#         url = reverse('upload')
#         self.assertEquals(resolve(url).func, upload)

#     def test_manage_url_resolves(self):
#         url = reverse('manage')
#         self.assertEquals(resolve(url).func, manage)

    # def test_delete_url_resolves(self):
    #     url = reverse('delete', args=['some-id'])
    #     self.assertEquals(resolve(url).func, delete)