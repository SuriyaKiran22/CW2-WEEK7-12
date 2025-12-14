class Dataset:
    """Represents a data science dataset in the platform."""
    
    def __init__(self, dataset_id: int, name: str, source: str, category: str, size: int):
        self.__id = dataset_id
        self.__name = name
        self.__source = source
        self.__category = category
        self.__size = size  # Size in KB
    
    def get_id(self) -> int:
        """Get dataset ID."""
        return self.__id
    
    def get_name(self) -> str:
        """Get dataset name."""
        return self.__name
    
    def get_source(self) -> str:
        """Get data source."""
        return self.__source
    
    def get_category(self) -> str:
        """Get dataset category."""
        return self.__category
    
    def get_size(self) -> int:
        """Get size in KB."""
        return self.__size
    
    def calculate_size_mb(self) -> float:
        """Calculate and return dataset size in megabytes."""
        return self.__size / 1024
    
    def to_dict(self) -> dict:
        """Convert dataset to dictionary for CSV export."""
        return {
            'id': self.__id,
            'name': self.__name,
            'source': self.__source,
            'category': self.__category,
            'size': self.__size
        }
    
    def __str__(self) -> str:
        size_mb = self.calculate_size_mb()
        return f"Dataset {self.__id}: {self.__name} ({size_mb:.2f} MB, {self.__category})"