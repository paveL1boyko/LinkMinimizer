import factory
from app.entities.short_url.short_url_entity import ShortURLEntity


class ShortURLEntityFactory(factory.Factory):
    long_url = factory.Faker("url")
    short_code = factory.LazyFunction(ShortURLEntity.generate_short_url)
    click_count = factory.Faker("random_int", min=0, max=1000)

    class Meta:
        model = ShortURLEntity
