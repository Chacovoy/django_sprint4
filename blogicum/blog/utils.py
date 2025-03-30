def filter_published(obj):

    return obj.filter(is_published=True)


def select_post_objects(obj):
    """ Takes Post model instance """
    return obj.objects.select_related(
        'author',
        'location',
        'category',
    )
