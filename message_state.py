import configs.types as types


class State:
    type: types.Types
    message: str
    tags: list
    
    def __init__(self):
        self.default()

    def default(self):
        self.type = None
        self.message = None
        self.tags = None