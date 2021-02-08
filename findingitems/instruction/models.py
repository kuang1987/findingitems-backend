from django.db import models
from django.contrib.postgres.fields import JSONField


# Create your models here.
class Instruction(models.Model):
    owner = models.ForeignKey(
        'users.AuthUser',
        related_name='instructions',
        on_delete=models.PROTECT,
    )
    INSTRUCTION_TYPE_STORE = 0
    INSTRUCTION_TYPE_SEARCH = 1
    INSTRUCTION_TYPE_CHOICES = (
        (INSTRUCTION_TYPE_STORE, 'store'),
        (INSTRUCTION_TYPE_SEARCH, 'search'),
    )
    type = models.PositiveSmallIntegerField(
        choices=INSTRUCTION_TYPE_CHOICES,
        default=INSTRUCTION_TYPE_STORE
    )
    audio_url = models.CharField(
        max_length=1024,
        blank=True,
        null=True
    )
    text = models.CharField(
        max_length=1024,
        blank=True,
        null=True
    )
    sdp_result = JSONField(
        null=True,
        blank=True,
    )
    create_time = models.DateTimeField(
        auto_now_add=True
    )
    item_part = models.CharField(
        max_length=1024,
        null=True,
    )
    loc_part = models.CharField(
        max_length=1024,
        blank=True,
    )
    is_delete = models.BooleanField(
        default=False
    )
