from rest_framework import serializers

from .models import User, Follow


class UsersSerializer(serializers.ModelSerializer):
    '''Cериализатор для управления пользователями.'''

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed',)
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed',)

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        '''Проверка на подписку.'''

        request = self.context.get('request')
        return (request.user.is_authenticated
                and Follow.objects.filter(user=request.user, author=obj)
                .exists())
