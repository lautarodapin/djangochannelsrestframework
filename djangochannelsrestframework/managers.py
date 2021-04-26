from typing import Iterable, List, Optional
from django.db.models import manager
from django.db.models.manager import Manager

from .signals import post_bulk_save

class CustomManager(Manager):

    def bulk_create(self, objs: Iterable[any], batch_size: Optional[int], ignore_conflicts: bool) -> List[any]:
        temp = super().bulk_create(objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts)
        print("bulk_create")
        for obj in objs:
            yield post_bulk_save.send(
                sender=obj.__class__,
                instance=obj,
                created=True,
            )
        return temp