import re
import uuid
from django.contrib.sessions.models import Session
from django.conf import settings
from rest_framework import serializers
from .models import ShortenedUrl


class ShortenSerializer(serializers.Serializer):
    link = serializers.URLField(max_length=settings.LINK_MAX_LENGTH, allow_null=False, allow_blank=False)
    shortened_id = serializers.CharField(max_length=settings.SHORTENED_MAX_LENGTH, required=False)
    session = serializers.CharField()

    @staticmethod
    def generate_id():
        return uuid.uuid4().hex[:8]

    def validate_session(self, val):
        return Session.objects.get(pk=val)

    def validate_shortened_id(self, val):
        if not re.match(r'^[0-9a-zA-Z]{1,8}$', val):
            raise serializers.ValidationError("shortened_id should consists of english characters or numbers")
        return val

    def validate(self, data):
        if not data.get('shortened_id', False):
            exists = True
            while exists:
                data['shortened_id'] = self.generate_id()
                exists = ShortenedUrl.objects.all().filter(shortened_id=data['shortened_id']).exists()

        else:
            if ShortenedUrl.objects.all().filter(shortened_id=data['shortened_id']).exists():
                self.shortened_url_obj = ShortenedUrl.objects.get(shortened_id=data['shortened_id'])
                if self.shortened_url_obj.session != data['session']:
                    raise serializers.ValidationError("such shortened_id already exists")
        return data

    def create(self, validated_data):
        if hasattr(self, 'shortened_url_obj'):
            self.shortened_url_obj.link = validated_data['link']
            self.shortened_url_obj.save()
            return self.shortened_url_obj
        else:
            return ShortenedUrl.objects.create(**validated_data)


class ShortenedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortenedUrl
        fields = ['shortened_id', 'link']



