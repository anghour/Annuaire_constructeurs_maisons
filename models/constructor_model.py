__author__= "Azziz ANGHOUR, TONTON_GROUP"
__email__= "anghour@gmail.com"
__version__= "1.0.0"


class Constructor:

    def __init__(self, intitule, dept_code, address, link, phone):
        self.intitule = intitule
        self.dept_code = dept_code
        self.address = address
        self.link = link
        self.phone= phone



    def __repr__(self):
        return str(self.__dict__)


class Departement:

    def __init__(self, name, link):
        self.name = name
        self.link = link


    def __repr__(self):
        return str(self.__dict__)




class Region:

    def __init__(self, name, link):
        self.name = name
        self.link = link


    def __repr__(self):
        return str(self.__dict__)

class Annuaire_Item:

    def __init__(self, intitule, region, departement, dept_code, address, phone, website):
        self.intitule = intitule
        self.region = region
        self.departement = departement
        self.departement_code = dept_code
        self.address = address
        self.phone = phone
        self.website = website

    def __repr__(self):
        return str(self.__dict__)

class Annuaire:

    def __init__(self):
        self.constructor_list = []

    def add_constructor(self, item):
        self.constructor_list.append(item)
