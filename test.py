from poetry_app.client import AppClient


client = AppClient()

print(client.get_index())
