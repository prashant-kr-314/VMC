from django import template
from datetime import date, timedelta

register = template.Library()

@register.filter(name='asci')
def asci_(n):
    MAX = 50
    # To store result (Excel column name)
    string = ["\0"]*MAX
 
    # To store current index in str which is result
    i = 0
    m = int(n)
    while m > 0:
        # Find remainder
        rem = m%26
 
        # if remainder is 0, then a 'Z' must be there in output
        if rem == 0:
            string[i] = 'Z'
            i += 1
            m = int(m/26)-1
        else:
            string[i] = chr(int(rem-1) + ord('A'))
            i += 1
            m = int(m/26)
    string[i] = '\0'
 
    # Reverse the string and print result
    string = string[::-1]
    return "".join(string)
