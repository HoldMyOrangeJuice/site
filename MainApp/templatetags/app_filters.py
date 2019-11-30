from django.template.defaulttags import register


@register.filter(name='get_item_')
def get_item_(iterable, i):
    i = int(i)
    iterable = list(iterable)
    #print(i)
    #print(iterable)
    return iterable[i]


@register.filter(name='create_name')
def create_name(x, y):
    return f"{x}a{y}"



