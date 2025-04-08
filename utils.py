import random
import string

def generate_short_code(length: int = 6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
