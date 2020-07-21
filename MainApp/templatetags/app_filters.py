from django.template.defaulttags import register


@register.filter(name='get_item_')
def get_item_(iterable, i):
    i = int(i)
    iterable = list(iterable)
    # print(i)
    # print(iterable)
    return iterable[i]


@register.filter(name='create_name')
def create_name(x, y):
    return f"{x}a{y}"


@register.filter(name='get_model_field')
def get_model_field(model, field):
    return model.__getattribute__(field)


@register.filter(name='inp_type')
def inp_type(index):
    if int(index) == 0:
        return "checkbox"
    else:
        return "text"

@register.filter(name='concatenate')
def get_model_field(s1, s2):
    return str(s1) + str(s2)

@register.filter(name='isint')
def isint(i):
    try:
        int(i)
        return True
    except:
        return False

@register.filter(name='toint')
def toint(i):
    return int(i)

@register.filter(name='get')
def get(dict, i):
    return dict.get(i)
