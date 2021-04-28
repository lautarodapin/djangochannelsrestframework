from typing import Dict, Optional, OrderedDict, Union
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
from django.db.models import Model, QuerySet 
from rest_framework import status

from .decorators import action
from djangochannelsrestframework.settings import api_settings


class CreateModelMixin:
    @action()
    def create(self, data, **kwargs):
        serializer = self.get_serializer(data=data, action_kwargs=kwargs)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, **kwargs)
        return serializer.data, status.HTTP_201_CREATED

    def perform_create(self, serializer, **kwargs):
        serializer.save()


class ListModelMixin:
    @action()
    def list(self, **kwargs):
        queryset = self.filter_queryset(self.get_queryset(**kwargs), **kwargs)

        if hasattr(self, "paginate_queryset"):
            page = self.paginate_queryset(queryset, **kwargs)
            if page is not None:
                serializer = self.get_serializer(
                    instance=page, many=True, action_kwargs=kwargs
                )
                return self.get_paginated_response(serializer.data), status.HTTP_200_OK

        serializer = self.get_serializer(
            instance=queryset, many=True, action_kwargs=kwargs
        )
        return serializer.data, status.HTTP_200_OK


class RetrieveModelMixin:
    @action()
    def retrieve(self, **kwargs):
        instance = self.get_object(**kwargs)
        serializer = self.get_serializer(instance=instance, action_kwargs=kwargs)
        return serializer.data, status.HTTP_200_OK


class UpdateModelMixin:
    @action()
    def update(self, data, **kwargs):
        instance = self.get_object(data=data, **kwargs)

        serializer = self.get_serializer(
            instance=instance, data=data, action_kwargs=kwargs, partial=False
        )

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer, **kwargs)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return serializer.data, status.HTTP_200_OK

    def perform_update(self, serializer, **kwargs):
        serializer.save()


class PatchModelMixin:
    @action()
    def patch(self, data, **kwargs):
        instance = self.get_object(data=data, **kwargs)

        serializer = self.get_serializer(
            instance=instance, data=data, action_kwargs=kwargs, partial=True
        )

        serializer.is_valid(raise_exception=True)
        self.perform_patch(serializer, **kwargs)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return serializer.data, status.HTTP_200_OK

    def perform_patch(self, serializer, **kwargs):
        serializer.save()


class DeleteModelMixin:
    @action()
    def delete(self, **kwargs):
        instance = self.get_object(**kwargs)

        self.perform_delete(instance, **kwargs)
        return None, status.HTTP_204_NO_CONTENT

    def perform_delete(self, instance, **kwargs):
        instance.delete()


class PaginatedModelListMixin(ListModelMixin):
    
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    @property
    def paginator(self) -> Optional[any]:
        """Gets the paginator class

        Returns:
            Pagination class. Optional.
        """
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(
        self, queryset: QuerySet[Model], **kwargs: Dict
    ) -> Optional[QuerySet]:
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(
            queryset, self.scope, view=self, **kwargs
        )

    def get_paginated_response(
        self, data: Union[ReturnDict, ReturnList]
    ) -> OrderedDict:
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

class StreamedPaginatedListMixin(PaginatedModelListMixin):
    
    async def handle_action(self, action: str, request_id: str, **kwargs):
        await super().handle_action(action, request_id, **kwargs)
        while self.paginator.offset < self.paginator.count:
            count = self.paginator.count
            limit = self.paginator.limit
            offset = self.paginator.offset
            kwargs["offset"] = limit + offset
            
            await super().handle_action(action, request_id, **kwargs)