class UserData:
    def __init__(self, state):
        self.state: str = state
        self.selected_city: str = None
        self.min_rooms: int = 0
        self.max_rooms: int = 0
        self.min_price: int = 0
        self.max_price: int = 0


    def __str__(self):
        return (f"UserData: state={self.state}, selected_city={self.selected_city}, min_rooms={self.min_rooms} "
                f", max_rooms={self.max_rooms}, min_price={self.min_price}, max_price={self.max_price}")
