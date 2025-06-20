import configs.config as config
import os

class TypeManager:
    def __init__(self):
        types_path = 'configs/types.conf'
        
        if config.TYPE_PATH:
            types_path = config.TYPE_PATH
        
        lines = ''
        
        if os.path.exists(types_path):
            with open(types_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        
        self.type_to_idx = {line.strip(): index for index, line in enumerate(lines)}
        self.idx_to_type = {index: line.strip() for index, line in enumerate(lines)}


    def type_to_string(self, idx: int):
        if idx in self.idx_to_type:
            return self.idx_to_type[idx]
        
        raise Exception('Тип не найден')

    def string_to_type(self, text: str):
        if text in self.type_to_idx:
            return self.type_to_idx[text]

        return None
    
    def get_types(self):
        return list(self.idx_to_type.keys())
