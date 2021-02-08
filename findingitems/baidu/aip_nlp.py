from aip import AipNlp
from django.conf import settings
import logging

logger = logging.getLogger('django.baidu.nlp')

ITEM_POSTAG_LIST = ['n', 'nw', 'nz']
DE_POSTAG_LIST = ['r', 'u', 'f']
NOUN_POSTAG_LIST = ['n', 'nw', 'nz', 'ns', 'u']


client = AipNlp(settings.BAIDU_APP_ID, settings.BAIDU_API_KEY, settings.BAIDU_SECRET_KEY)


def parse(text):
    result = {}

    options = {
        'mode': 1
    }

    try:
        r = client.depParser(text, options)
        result['dep'] = r['items']
    except Exception as e:
        logger.error('baidu nlp api error. Text: %s, error: %s' % (text, str(e)))

    return result


def concat(words):
    if len(words) == 0:
        return []

    last_id = words[0]['id']
    phrase = []
    temp = []
    temp.append(words[0]['word'])
    for w in words[1:]:
        if w['id'] != last_id + 1:
            phrase.append(('').join(temp))
            temp = []

        temp.append(w['word'])
        last_id = w['id']

    phrase.append(('').join(temp))

    return phrase


def abstract(dep_result):
    item_part = []
    loc_part = []
    is_hed = False
    item = []
    loc = []

    for i in dep_result:
        if i['deprel'] == 'HED':
            is_hed = True
            continue

        if is_hed:
            loc_part.append(i)
        else:
            item_part.append(i)


    for i in item_part:
        if (i['postag'] in ITEM_POSTAG_LIST) or (i['postag'] in DE_POSTAG_LIST and i['deprel'] == 'DE'):
            item.append(i)

    for i in loc_part:
        if (i['postag'] in ITEM_POSTAG_LIST) or (i['postag'] in DE_POSTAG_LIST and i['deprel'] == 'DE'):
            loc.append(i)

    final_item = concat(item)
    final_loc = ('').join([ w['word'] for w in loc])

    return final_item, final_loc


def abstract_v1(dep_result):
    item_part = []
    loc_part = []
    is_hed = False
    # item = []
    # loc = []

    for i in dep_result:
        if i['deprel'] == 'HED':
            is_hed = True
            continue

        if is_hed:
            loc_part.append(i)
        else:
            item_part.append(i)


    # for i in item_part:
    #     if (i['postag'] in ITEM_POSTAG_LIST) or (i['postag'] in DE_POSTAG_LIST and i['deprel'] == 'DE'):
    #         item.append(i)
    #
    # for i in loc_part:
    #     if (i['postag'] in ITEM_POSTAG_LIST) or (i['postag'] in DE_POSTAG_LIST and i['deprel'] == 'DE'):
    #         loc.append(i)

    final_item = ('').join([ w['word'] for w in item_part])
    final_loc = ('').join([ w['word'] for w in loc_part])

    return final_item, final_loc


def abstract_entity(dep_result):
    item_part = []
    loc_part = []
    is_hed = False
    item = []
    phrase_candidates = []
    # loc = []

    for i in dep_result:
        if i['deprel'] == 'HED':
            is_hed = True
            continue

        if is_hed:
            loc_part.append(i)
        else:
            item_part.append(i)

    # get all noun in item part
    for i in item_part:
        if (i['postag'] in ITEM_POSTAG_LIST):
            item.append(i['word'])

    for i in item_part:
        if (i['postag'] in ITEM_POSTAG_LIST) or (i['postag'] in DE_POSTAG_LIST and i['deprel'] == 'DE'):
            phrase_candidates.append(i)

    phrase = concat(phrase_candidates)
    item.extend(phrase)

    return item


