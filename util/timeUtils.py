from datetime import time

def in_killzone(current_dt):
    current_time = current_dt.time()
    london_killzone = time(3, 0) <= current_time <= time(6, 0)
    ny_killzone = time(12, 0) <= current_time <= time(15, 0)
    return london_killzone or ny_killzone