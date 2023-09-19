

import uuid
from dataclasses import dataclass

@dataclass
class Image:
    id: uuid
    wall_id: uuid 
    
    