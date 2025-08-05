from abc import ABC, abstractmethod
from typing import Dict

class MetaApiOutputPort(ABC):
    @abstractmethod
    def send_message(self, payload: Dict) -> Dict:
        pass
