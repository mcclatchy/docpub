from documentcloud import DocumentCloud
from docpub.settings_private import DC_USERNAME, DC_PASSWORD
# from .models import DocumentCloudCredentials


# documentcloud_password = DocumentCloudCredentials.password

# if not documentcloud_password:
username = DC_USERNAME
password = DC_PASSWORD

client = DocumentCloud(username, password)

# def client(username, password):
#     client = DocumentCloud(username, password)
#     return client