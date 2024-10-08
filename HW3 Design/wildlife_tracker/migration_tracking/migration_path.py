from typing import Any
from wildlife_tracker.habitat_management.habitat import Habitat

class MigrationPath:

    def __init__(self, 
                path_id: int,
                size: int,
                species: str,
                start_date: str,
                start_location: Habitat) -> None:
        self.path_id = path_id
        self.size = size
        self.species = species
        self.start_date = start_date
        self.start_location = start_location


    def update_migration_path_details(self, **kwargs: dict[str: Any]) -> None:
        pass

    def get_migration_path_details(self) -> dict:
        pass