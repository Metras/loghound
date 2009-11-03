"""
progtablegen generates WMBR's programming tables. It consists of one function:
make_day_tables
"""

import reportlab
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import PageBreak
from reportlab.lib.units import inch 
from datetime import datetime

########### table parameters 
NOTES = 'NOTES' 
HEADER_ROW = [
    "Time On",
    "Time Off",
    "Program Material:"
]
NUM_COLS = len(HEADER_ROW)

# reportlab uses 'None' in this context to mean: autofit
HEADER_ROW_HEIGHT = None
COL_WIDTHS = [None]*NUM_COLS

# note: reportlab uses column-row cell coordinates, aka excel "A1" style. 
TABLE_BASE_STYLE = [
    ('VALIGN', (0,0), (-1,0), 'TOP'),
    ('ALIGN', (0,0), (-1,0), 'CENTER'),
    ('GRID', (0,0), (-1,-1), .6, colors.black),
    ('BOX',(0,0),(-1,-1),2,colors.black),
    ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
    ('ALIGN', (0,1), (0, -1), 'CENTER'),
    ('VALIGN', (0,1), (0, -1), 'MIDDLE'),
]

########### API 
def make_prog_table(events):
  rvalue = []
  for event in events:
    if event[1] == "show":
      rvalue.append(Table([event[3]]))
    elif event[1] == "altshow":
      pass
    else:
      pass
  return rvalue

#########

class show:
    def __init__(self, start, duration, engineer, producer, announcer):
        self.start = start
        self.duration = duration
        self.engineer = engineer
        self.producer = producer
        self.announcer = announcer
        
class signon:
    def __init__(self, time):        
        self.time = time
        
class signoff:
    def __init__(self, time):
        self.time = time

def make_day_tables(showsAndEvents):
    '''
    showsAndEvents: a list of show, signon and signoff objects
    returns a list of tables, one table per page. 
    '''
    cwidths = [1*inch]+[3*inch, 3*inch]
    rheights= [40]*22
    
    data = [
        ['00:00-02:00', 'Algorhythms', ''],
        ['Engineer:', 'Wally Shmally', ''],
        ['Producer:', 'Adam Bockelie, Ka Man Chan, Tracey Hayse, Elizabeth Jones', ''],
        ['Announcer:', 'Adam Bockelie, Ka Man Chan, Tracey Hayse, Elizabeth Jones', ''],
        ['anytime', 'PSA:', 'Certified:'],
        ['01:00', 'Station ID', 'Certified:'],
        ['anytime', 'Promo:', 'Certified:'],
        ['02:00', 'Station ID:', 'Certified:'],
        
        ['02:00-03:00', 'Music For Human Beings', ''],
        ['Engineer:', 'Bob Jobs', ''],
        ['Producer:', 'Linda Pinkow, Chuck Rosina', ''],
        ['Announcer:', 'Mistress Laura', ''],
        ['anytime', 'PSA:', 'Certified:'],
        ['03:00', 'Station ID', 'Certified:'],
        
        ['03:00-05:00', 'The Choice is Yourz', ''],
        ['Engineer:', 'Rik', ''],
        ['Producer:', 'Rik', ''],
        ['Announcer:', 'Rik', ''],        
        ['anytime', 'Promo:', 'Certified:'],
        ['04:00', 'Station ID', 'Certified:'],
        ['anytime', 'PSA:', 'Certified:'],
        ['05:00', 'Station ID', 'Certified:'],                
    ]
    
    story=[]
    story.append(Table(data, cwidths, rheights))
    doc = SimpleDocTemplate("prog_table_test.pdf")     
    doc.build(story)

make_day_tables([])

    