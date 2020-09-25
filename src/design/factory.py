# coding = utf-8
"""factory design pattern"""


class Product(object):
    """a product may have many features"""

    def __init__(self):
        """setup product features"""
        pass

    @classmethod
    def create(cls):
        """
        class method can be considered as a basic factory function
            to help create single product instance
        """
        return cls()


class Factory(object):
    """use factory to create product"""

    def __init__(self):
        """setup factory settings for product creation"""
        pass

    def create_products(self):
        """prepare data, make product instances, and return them"""
        # return Product()
        # return [Product()]
        # return Product.create()
        # return [Product.create()]
        pass


# here follows a detail example


class MyProduct(object):

    def __init__(self, prod_name, prod_type, prod_owner):
        self.name = prod_name
        self.type = prod_type
        self.owner = prod_owner

    @classmethod
    def create(cls, prod_name, prod_type):
        """generate product owner automatically"""
        prod_owner = 'somebody'
        return cls(
            prod_name=prod_name,
            prod_type=prod_type,
            prod_owner=prod_owner,
        )


class MyFactory(object):

    def __init__(self, fac_type, fac_owner):
        """factory type and owner for product creation"""
        self.type = fac_type
        self.owner = fac_owner

    def generate_products(self, name_list):
        """use factory settings to create new products"""
        return [MyProduct(
            prod_name=name,
            prod_type=self.type,
            prod_owner=self.owner,
        ) for name in name_list]

    @classmethod
    def recall_db_products(cls, db_model):
        """
        recall products whose info are stored in database
        this method does not depend on factory settings
            so it is set as classmethod
        """
        prod_data = db_model.product_data()
        return [MyProduct(
            prod_name=each_data['name'],
            prod_type=each_data['type'],
            prod_owner=each_data['owner'],
        ) for each_data in prod_data]
