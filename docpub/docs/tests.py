import time
from django.test import TestCase
from django.contrib.auth.models import User
from docs.connection import connection
from docs.decryption import decryption
from docs.models import Document, DocumentCloudCredentials
from docpub.settings import CONVERT, DC_USERNAME, DC_PASSWORD, TEST_PDF


class DocumentTestCase(TestCase):
    def setUp(self):
        ## create a test doc
        Document.objects.create(
            access='organization',
            title='testdoc',
            link=TEST_PDF
        )
        ## create a test user
        User.objects.create(
            first_name='Firstnametest',
            last_name='Lastnametest',
            username='firstnamelastname'
        )
        test_user = User.objects.get(username='firstnamelastname')
        ## create test creds
        DocumentCloudCredentials.objects.create(
            password='testpassword',
            user=test_user
        )

    def test_encrypt_password(self):
        print('\n----- TEST ENCRYPT PASSWORD -----\n')
        test_user = User.objects.get(username='firstnamelastname')
        creds = DocumentCloudCredentials.objects.get(user=test_user)
        print('Encrypted password: ' + creds.password)

        password_decrypted = decryption(creds.password)
        creds.password = password_decrypted
        print('\nDecrypted password: ' + password_decrypted)

    def test_documentcloud(self):
        print('\n----- TEST DOCUMENT CLOUD -----\n')
        doc = Document.objects.get(title='testdoc')
        kwargs = {
            'title': doc.title,
            'access': doc.access,
        }
        client = connection(DC_USERNAME, DC_PASSWORD)
        obj = client.documents.upload(doc.link, **kwargs)
        obj.put()
        print('Doc added: ' + str(obj.title))
        ## add the DocumentCloud id to the document ID
        doc.documentcloud_id = obj.id
        doc.save()

        seconds = 3
        print('\nSleeping for {} seconds\n'.format(seconds))
        time.sleep(seconds)

        client = connection(DC_USERNAME, DC_PASSWORD)
        obj = client.documents.get(doc.documentcloud_id)
        obj.description = 'test description'
        obj.put()
        print('Doc description updated: ' + obj.description)

        seconds = 3
        print('\nSleeping for {} seconds\n'.format(seconds))
        time.sleep(seconds)

        obj.delete()
        print('Doc deleted on DocumentCloud\n')


