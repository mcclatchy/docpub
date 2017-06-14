from documentcloud import DocumentCloud
# from docpub.settings import DC_USERNAME, DC_PASSWORD


def connection(username, password):
  client = DocumentCloud(username, password)
  return client
