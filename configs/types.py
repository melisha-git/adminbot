from enum import Enum

class Types(Enum):
    NEW_KNOWELAGE = 1
    SETUP = 2
    CRIB = 3
    READ = 4

def type_to_string(type: Types):
    
    if type == Types.NEW_KNOWELAGE:
        return 'Новый термин 😶:'
    elif type == Types.SETUP:
        return 'Настраиваем 🚀:'
    elif type == Types.CRIB:
        return 'Шпаргалка 👾:'
    elif type == Types.READ:
        return 'Что почитать ☠️?'
    
    raise Exception('Тип не найден')

def string_to_type(text: str):
    if text == 'Новый термин 😶:':
        return Types.NEW_KNOWELAGE
    elif text == 'Настраиваем 🚀:':
        return Types.SETUP
    elif text == 'Шпаргалка 👾:':
        return Types.CRIB
    elif text == 'Что почитать ☠️?':
        return Types.READ
    
    return None
