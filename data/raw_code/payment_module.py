
    def process_payment(amount, currency, user_status):
        # Business Rule 1: Min amount is 10
        if amount < 10:
            return {"error": "Min amount 10"}
            
        # Business Rule 2: VIP users get 5% discount
        if user_status == "VIP":
            amount = amount * 0.95
            
        # Dependency: Bank API
        if connect_bank_api(amount, currency):
            return {"status": "Success", "charged": amount}
            
        return {"error": "Bank timeout"}
    