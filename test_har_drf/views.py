from django import http
from django.contrib.auth import models

from rest_framework import status
from rest_framework import viewsets

from test_har_drf import serializers


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = models.User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer

    def create(self, request, *args, **kwargs):
        """
        Support returning non-JSON.
        """
        if 'json' not in request.META['headers']['Accept']:
            # Return the original POST data
            return http.HttpResponse(
                'Foo plain text body', status=status.HTTP_201_CREATED,
                content_type='text/plain')

        return super(UserViewSet, self).create(request, *args, **kwargs)
