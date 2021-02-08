from django.db import models

# Create your models here.


class Item(models.Model):
    instruction = models.ForeignKey(
        'instruction.Instruction',
        related_name='items',
        on_delete=models.PROTECT,
        null=True,
    )
    name = models.CharField(
        max_length=1024,
    )
    loc = models.CharField(
        max_length=1024,
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
    )
