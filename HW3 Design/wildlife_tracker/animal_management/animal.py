from typing import Any, Optional

class Animal:

    def __init__(self, 
                age: Optional[int] = None, 
                animal_id: int, 
                health_status: Optional[str] = None) -> None:
        self.animal_id = animal_id
        self.age = age or []
        self.health_status = health_status or []
        pass


    def get_animal_details(self) -> dict[str, Any]:
        pass

    def update_animal_details(self, **kwargs: dict[str: Any]) -> None:
        pass

