from api_clients.rise import RiseApiClient
from entries.models import RiseEntry
from users.models import User


class RiseAppService:
    @staticmethod
    def get_client(user: User):
        return RiseApiClient(user=user)

    def create_entry(self, rise_entry: RiseEntry) -> None:
        rise_client = self.get_client(user=rise_entry.entry.user)
        rise_client.create_entry(rise_entry=rise_entry)

    def update_entry(self, rise_entry: RiseEntry) -> None:
        rise_client = self.get_client(user=rise_entry.entry.user)
        rise_client.update_entry(rise_entry=rise_entry)

    def delete_entry(self, rise_entry: RiseEntry) -> None:
        rise_client = self.get_client(user=rise_entry.entry.user)
        rise_client.delete_entry(rise_entry=rise_entry)
