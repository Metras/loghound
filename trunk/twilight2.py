# parsing twilight data from the government is easy

import urllib
import urllib2
url = 'http://aa.usno.navy.mil/cgi-bin/aa_pap.pl'

# note: can't use a dictionary as is standard practice with urllib2. 
# the US Navy craps out when POST parameters are in random order.   
data = [
    ('ID', 'WMBR'),
    ('xxy', 2009),
    ('xxm', 10),
    ('xxd', 28),
    ('st', 'MA'),
    ('place', 'cambridge'),
]

data = urllib.urlencode(data)
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
the_page = response.read()

print the_page
