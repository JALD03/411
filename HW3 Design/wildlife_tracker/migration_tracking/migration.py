from typing import Any, Optional
from wildlife_tracker.migration_tracking.migration_path import MigrationPath
from wildlife_tracker.habitat_management.habitat import Habitat

class Migration:

    def __init__(self, 
                current_date: str, 
                current_location: str,
                destination: Habitat, 
                duration: Optional[int] = None, 
                migration_id: int,
                migration_path: MigrationPath, 
                species: str, 
                status: str = "Scheduled") -> None:
        self.migration_id = migration_id
        self.current_date = current_date
        self.current_location = current_location
        self.destination = destination
        self.duration = duration
        self.migration_path = migration_path
        self.species = species
        self.status = status

    def get_migration_details(self) -> dict[str, Any]:
        pass

    def update_migration_details(self, **kwargs: dict[str: Any]) -> None:
        pass

