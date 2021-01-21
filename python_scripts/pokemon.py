class pokemon:
    def __init__(self, regional = None, national = None, name = None, type1 = None, type2 = None, region = None, emote = None, shiny_emote = None):
        self.regional_number = regional
        self.national_number = national
        self.name = name
        self.type1 = type1
        self.type2 = type2
        self.region = region
        self.emote = emote
        self.shiny_emote = shiny_emote

    def get_from_string(self, pokestring):
        if len(pokestring) == 0:
            return False
        temp_array = pokestring.split("\t")
        self.regional_number = temp_array[0]
        self.national_number = temp_array[1]
        self.name = temp_array[2]
        self.region = temp_array[3]
        self.type1 = temp_array[4]
        if len(temp_array) > 7:
            self.type2 = temp_array[5]
            self.emote = temp_array[6]
            self.shiny_emote = temp_array[7]
        else:
            self.type2 = None
            self.emote = temp_array[5]
            self.shiny_emote = temp_array[6]
        if self.emote == "<None>":
            self.emote = None
        if self.shiny_emote == "<None>":
            self.shiny_emote = None
        return True

    def set_region(self):
        if self.regional_number == "ALO":
            self.region = "Alola"
            return "Alola"
        if self.regional_number == "GAL":
            self.region = "Galar"
            return "Galar"
        if int(self.national_number) <= 0:
            self.region = "Unknown"
        elif int(self.national_number) <= 151:
            self.region = "Kanto"
        elif int(self.national_number) <= 251:
            self.region = "Johto"
        elif int(self.national_number) <= 386:
            self.region = "Hoenn"
        elif int(self.national_number) <= 493:
            self.region = "Sinnoh"
        elif int(self.national_number) <= 649:
            self.region = "Unova"
        elif int(self.national_number) <= 721:
            self.region = "Kalos"
        elif int(self.national_number) <= 809:
            self.region = "Alola"
        elif int(self.national_number) <= 898:
            self.region = "Galar"
        else:
            self.region = "Unknown"
        return self.region

    def regional_variant(self):
        return len(self.national_number) > 3

    def dual_type(self):
        return not self.type2 == None

    def to_string(self):
        string = self.regional_number
        string = string + "\t" + self.national_number
        string = string + "\t" + self.name
        string = string + "\t" + self.region
        string = string + "\t" + self.type1
        if self.dual_type():
            string = string + "\t" + self.type2
        if self.emote == None:
            string = string + "\t<None>"
        else:
            string = string + "\t" + self.emote
        if self.shiny_emote == None:
            string = string + "\t<None>"
        else:
            string = string + "\t" + self.shiny_emote
        return string
