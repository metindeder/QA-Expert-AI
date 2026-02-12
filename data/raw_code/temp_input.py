def process_payment(amount, user_status):
    # Business Rule: Min 10 TL
    if amount < 10:
        return False
    
    # Dependency: Bank API Check
    if check_bank_api(amount):
        return True
    return False