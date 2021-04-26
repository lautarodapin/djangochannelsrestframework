import asyncio

import pytest
from channels import DEFAULT_CHANNEL_LAYER
from channels.db import database_sync_to_async
from channels.layers import channel_layers
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model, user_logged_in
from rest_framework import serializers

from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin
from tests.models import TestModel

from djangochannelsrestframework.signals import post_bulk_save
from django.dispatch import receiver
from .models import TestModel

from django.db.models import signals
from django.dispatch import receiver

@pytest.mark.django_db(transaction=True)
def test_bulk_create_signal(settings):
    data = []
    def señal(sender, instance, **kwargs):
        print(instance)
        data.append(instance)

    post_bulk_save.connect(señal, weak=False)

    TestModel.objects.create(name="test 1")
    # assert data[0] == "test 1"
    assert TestModel.objects.first().name == "test 1"
    assert len(data) == 1