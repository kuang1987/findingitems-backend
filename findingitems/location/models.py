from django.db import models

# Create your models here.


class Location(models.Model):
    owner = models.ForeignKey(
        'users.AuthUser',
        related_name='locations',
        on_delete=models.PROTECT,
    )
    name = models.CharField(
        max_length=256,
        default='我的家'
    )
    is_default = models.BooleanField(
        default=True
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
    )

    def get_members(self):
        return [m.member for m in self.memberships.filter(role=LocationMemberShip.LOCATION_MEMBER_ROLE_MEMBER)]


class LocationMemberShip(models.Model):
    location = models.ForeignKey(
        'location.Location',
        related_name='memberships',
        on_delete=models.CASCADE,
    )
    member = models.ForeignKey(
        'users.AuthUser',
        related_name='joined_locations',
        on_delete=models.CASCADE,
    )
    LOCATION_MEMBER_ROLE_OWNER = 0
    LOCATION_MEMBER_ROLE_MEMBER = 1
    LOCATION_MEMBER_ROLE_CHOICES = (
        (LOCATION_MEMBER_ROLE_OWNER, 'owner'),
        (LOCATION_MEMBER_ROLE_MEMBER, 'member'),
    )
    role = models.PositiveSmallIntegerField(
        default=LOCATION_MEMBER_ROLE_MEMBER,
        choices=LOCATION_MEMBER_ROLE_CHOICES,
    )
    alias_name = models.CharField(
        max_length=128,
        default=''
    )

    def get_location_owner(self):
        return self.location.owner

    def get_location_members(self):
        return self.location.get_members()


class LocationMemberInvitation(models.Model):
    location = models.ForeignKey(
        'location.Location',
        related_name='invitations',
        on_delete=models.CASCADE,
    )
    LOCATION_INVITATION_STATUS_PENDING = 0
    LOCATION_INVITATION_STATUS_CONFIRM = 1
    LOCATION_INVITATION_STATUS_REJECT = 2
    LOCATION_INVITATION_STATUS_CHOICES = (
        (LOCATION_INVITATION_STATUS_PENDING, 'pending'),
        (LOCATION_INVITATION_STATUS_CONFIRM, 'confirm'),
        (LOCATION_INVITATION_STATUS_REJECT, 'reject'),
    )
    status = models.PositiveSmallIntegerField(
        default=LOCATION_INVITATION_STATUS_PENDING,
        choices=LOCATION_INVITATION_STATUS_CHOICES,
    )
    member = models.ForeignKey(
        'users.AuthUser',
        related_name='invitations',
        on_delete=models.CASCADE,
    )
    update_date = models.DateTimeField(
        auto_now=True
    )
