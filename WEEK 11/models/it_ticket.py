class ITTicket:
    """Represents an IT support ticket."""
    
    def __init__(self, ticket_id: int, title: str, priority: str, status: str, created_date: str):
        self.__id = ticket_id
        self.__title = title
        self.__priority = priority
        self.__status = status
        self.__created_date = created_date
    
    def get_id(self) -> int:
        """Get ticket ID."""
        return self.__id
    
    def get_title(self) -> str:
        """Get ticket title."""
        return self.__title
    
    def get_priority(self) -> str:
        """Get priority level."""
        return self.__priority
    
    def get_status(self) -> str:
        """Get current status."""
        return self.__status
    
    def get_created_date(self) -> str:
        """Get creation date."""
        return self.__created_date
    
    def update_status(self, new_status: str) -> None:
        """Update ticket status."""
        self.__status = new_status
    
    def get_priority_level(self) -> int:
        """Return an integer priority level for comparison."""
        mapping = {"low": 1, "medium": 2, "high": 3, "urgent": 4}
        return mapping.get(self.__priority.lower(), 0)
    
    def to_dict(self) -> dict:
        """Convert ticket to dictionary for CSV export."""
        return {
            'id': self.__id,
            'title': self.__title,
            'priority': self.__priority,
            'status': self.__status,
            'created_date': self.__created_date
        }
    
    def __str__(self) -> str:
        return f"Ticket {self.__id}: {self.__title} [{self.__priority}] – {self.__status}"