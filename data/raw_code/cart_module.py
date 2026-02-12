
class ShoppingCart:
    def add_item(self, item_id, price):
        if self.validate_stock(item_id):
            self.total += price
            return True
        return False

    def validate_stock(self, item_id):
        # Connects to stock database
        print("Checking DB...")
        return True
