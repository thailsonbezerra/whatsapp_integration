from abc import ABC, abstractmethod
from app.core.domain.models import SendMessagePayload, StatusPayload
from typing import Dict

class SendMessageInputPort(ABC):
    @abstractmethod
    def execute(self, payload: SendMessagePayload) -> Dict:
        pass

class SendStatusInputPort(ABC):
    @abstractmethod
    def execute(self, payload: StatusPayload) -> Dict:
        pass
