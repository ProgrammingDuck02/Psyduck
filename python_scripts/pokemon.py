class pokemon:
    def __init__(self):
        self.regional_number = None
        self.national_number = None
        self.name = None
        self.region = None
        self.type1 = None
        self.type2 = None

    def __init__(self, regional, national, name, region, type1, type2 = None):
        self.regional_number = regional
        self.national_number = national
        self.name = name
        self.region = region
        self.type1 = type1
        self.type2 = type2

    def get_from_string(self, pokestring):
        temp_array = pokestring.split("\t")
        self.regional_number = temp_array[0]
        self.national_number = temp_array[1]
        self.name = temp_array[2]
        self.type1 = temp_array[3]
        if len(temp_array) > 4:
            self.type2 = temp_array[4]
        else:
            self.type2 = None

    def set_region(self):
        if self.national_number <= 0:
            self.region = "Unknown"
        elif self.national_number <= 151:
            self.region = "Kanto"
        elif self.national_number <= 251:
            self.region = "Johto"
        elif self.national_number <= 386:
            self.region = "Hoenn"
        elif self.national_number <= 493:
            self.region = "Sinnoh"
        elif self.national_number <= 649:
            self.region = "Unova"
        elif self.national_number <= 721:
            self.region = "Kalos"
        elif self.national_number <= 809:
            self.region = "Alola"
        elif self.national_number <= 898:
            self.region = "Galar"
        else:
            self.region = "Unknown"
        return self.region

    def dual_type(self):
        return not self.type2 == None