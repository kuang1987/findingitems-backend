from rest_framework.viewsets import GenericViewSet
from findingitems.api.generics import *
from rest_framework.decorators import action
from .serializers import InstructionListSerializer
from findingitems.instruction.models import Instruction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response

from findingitems.api.permissions import IsUserAuthenticated
from findingitems.baidu.aip_nlp import (
    parse as nlp_parse,
    abstract_v1 as nlp_abs,
)
from findingitems.instruction.utils import search_instructions
from findingitems.location.models import Location
from findingitems.api.exceptions.common import ParameterInvalid
from findingitems.api.exceptions import error_msg


class InstructionViewSet(CreateModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = [IsUserAuthenticated,]
    lookup_url_kwarg = "instruction_id"
    filterset_fields = ['location']

    def get_serializer_class(self):
        return InstructionListSerializer

    def get_queryset(self):
        location_mems = self.request.user.joined_locations.all()
        location_ids = [lm.location.id for lm in location_mems]
        return Instruction.objects.filter(
            is_delete=False,
            type=Instruction.INSTRUCTION_TYPE_STORE,
            location_id__in=location_ids,
        ).order_by('-create_time')

    def perform_create(self, serializer):
        loc_id = serializer.validated_data.get('location_id', -1)
        loc_obj = None
        try:
            loc_obj = Location.objects.get(id=loc_id)
        except ObjectDoesNotExist:
            if serializer.validated_data['type'] == Instruction.INSTRUCTION_TYPE_STORE:
                raise ParameterInvalid(error_msg.LOCATION_PARAMETER_MISSING)

        sdp_result = nlp_parse(serializer.validated_data['text'])
        item, loc = nlp_abs(sdp_result['dep'])
        serializer.save(
            item_part=item,
            loc_part=loc,
            sdp_result=sdp_result,
            owner=self.request.user,
            location=loc_obj
        )
        # item, loc = nlp_abs(sdp_result['dep'])
        # # for item in items:
        # item_instance = Item.objects.create(
        #     name=item,
        #     loc=loc
        # )
        # item_instance.save()

    @action(methods=['post'], detail=False)
    def add(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()

    @action(methods=['post'], detail=True)
    def remove(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    @action(methods=['get'], detail=False)
    def search(self, request, *args, **kwargs):
        instruction_id = request.query_params.get('instruction_id', -1)
        try:
            finding_obj = Instruction.objects.get(id=instruction_id)
        except ObjectDoesNotExist:
            return Response({'code': 0,
                             'error_msg': '',
                             'data': {
                                "count": 0,
                                "next": None,
                                "previous": None,
                                "results": []
                             }
                           }, status=status.HTTP_200_OK)

        store_instances = self.get_queryset()
        items = search_instructions(finding_obj, store_instances)
        for item in items:
            print(item.text)
        page = self.paginate_queryset(items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(items, many=True)
        return Response({"code": 0, "data": serializer.data, "error_msg": ""})


