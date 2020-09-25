# coding = utf-8
"""descriptor"""


class Descriptor(object):
    """descriptor can easily create similar properties"""

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        instance.__dict__.pop(self.name)


class TargetObject(object):
    key = Descriptor()
    value = Descriptor()

    def __init__(self, key, value):
        self.key = key
        self.value = value


class TypeValidateDescriptor(Descriptor):
    """
    can define more complicated descriptor
    for example: validate value type for setter
    """

    def __init__(self, valid_type=None):
        self.valid_type = valid_type

    def __set__(self, instance, value):
        if self.valid_type:
            assert isinstance(value, self.valid_type)
        super().__set__(instance, value)


class AnotherTargetObject(object):
    key = TypeValidateDescriptor(str)
    value = TypeValidateDescriptor(int)

    def __init__(self, key, value):
        self.key = key
        self.value = value


if __name__ == '__main__':
    to_1 = TargetObject('a', 1)
    to_2 = TargetObject('b', 2)
    print(to_1.key)
    print(to_1.value)
    print(to_2.key)
    print(to_2.value)

    to_3 = AnotherTargetObject('a', 1)
    print(to_3.key)
    print(to_3.value)
    to_4 = AnotherTargetObject('a', '1')  # this will cause an exception
