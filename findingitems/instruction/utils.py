from .models import Instruction
from findingitems.baidu.aip_nlp import abstract_entity
import re


def search_instructions(finding_obj, store_queryset):
    items = []
    max_score = 0
    finding_entity_list = abstract_entity(finding_obj.sdp_result.get('dep', []))
    print(finding_entity_list)
    for item in store_queryset:
        score = 0
        for entity in finding_entity_list:
            if re.search(entity, item.text, re.I):
                score = score + 1

        if score > 0:
            if score > max_score:
                items.insert(0, item)
                max_score = score
            else:
                items.append(item)

        print([item.id for item in items])
        print(score)

    return items



