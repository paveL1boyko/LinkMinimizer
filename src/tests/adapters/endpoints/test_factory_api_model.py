import factory
from app.frameworks_and_drivers.api_models import URLPayload


class URLPayloadFactory(factory.Factory):
    long_url = factory.Faker("url")

    class Meta:
        model = URLPayload
