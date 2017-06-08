from documentcloud import DocumentCloud
from docpub.settings_private import DC_USERNAME, DC_PASSWORD


username = DC_USERNAME
password = DC_PASSWORD

client = DocumentCloud(username, password)