def check_temp_alarm(current_temp, duration):
    # Rule: Above 8°C for more than 15 mins
    if current_temp > 8 and duration > 15:
        return "ENV_ALARM"
    return "NORMAL"

def process_dispatch(item_batch, oldest_batch_in_stock):
    # Rule: FEFO - First Expired First Out
    if item_batch > oldest_batch_in_stock:
        return "BLOCK: FEFO Violation"
    return "SUCCESS"