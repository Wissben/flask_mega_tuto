from flask import current_app


def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    mask = {}
    for field in model.__searchable__:
        mask[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, body=mask, id=model.id)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=inde, id=model.id)


def query_index(index, query, page=1, page_size=20):
    if not current_app.elasticsearch:
        return
    result = current_app.elasticsearch.search(
        index=index,
        body={
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['*']
                }
            },
            'from': (page - 1) * page_size,
            'size': page_size
        }
    )
    ids = [int(hit['_id']) for hit in result['hits']['hits']]
    return ids, result['hits']['total']['value']
