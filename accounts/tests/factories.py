import factory
from django.contrib.auth import get_user_model

User = get_user_model()

DEFAULT_PASSWORD = "Sup3rStr0ng!pw"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = "Test"
    last_name = "User"

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        obj.set_password(extracted or DEFAULT_PASSWORD)
        if create:
            obj.save()
