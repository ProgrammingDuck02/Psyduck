class move:
    def __init__(self, id = None, name = None, type = None, category = None, power = None, accuracy = None, PP=None, effect = None, description = None, can_use = None):
        self.id = id
        self.name = name
        self.type = type
        self.power = power
        self.category = category
        self.accuracy = accuracy
        self.PP = PP
        self.effect = effect
        self.description = description
        self.can_use = can_use