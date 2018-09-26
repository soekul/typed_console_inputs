class StandardCastMixin(object):
    type_class = int
    type_class_args = []
    type_class_kwargs = {}

    def __init__(self, *args, **kwargs):
        attribs = ['type_class', 'type_class_args', 'type_class_kwargs']
        for attr in attribs:
            if attr in kwargs:
                setattr(self, attr, kwargs.pop(attr))

        super(StandardCastMixin, self).__init__(*args, **kwargs)

    def convert_value(self, value):
        return self.type_class(
            super(StandardCastMixin, self).convert_value(value),
            *self.type_class_args,
            **self.type_class_kwargs
        )


class RemoveCharsMixin(object):
    chars_to_remove = []

    def __init__(self, *args, **kwargs):
        if 'chars_to_remove' in kwargs:
            self.chars_to_remove = kwargs.pop('chars_to_remove')
        super(RemoveCharsMixin, self).__init__(*args, **kwargs)

    def convert_value(self, value):
        ret_val = super(RemoveCharsMixin, self).convert_value(value)
        for char in self.chars_to_remove:
            ret_val = ret_val.replace(char, '')
        return ret_val