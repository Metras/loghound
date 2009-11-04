"""
progtablegen generates WMBR's programming tables. It consists of one function:
make_day_tables
"""

# import reportlab
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
# from reportlab.platypus import BaseDocTemplate, Frame, NextPageTemplate, PageBreak, PageTemplate, Table, TableStyle, Paragraph, flowables
# from reportlab.lib.units import inch 
# from datetime import datetime

import os
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, SimpleDocTemplate, Frame, NextPageTemplate, PageBreak, PageTemplate, Table, TableStyle, Paragraph, Spacer, flowables
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
import tablegen
from pprint import pprint

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


styles=getSampleStyleSheet() 


from progheader import make_header_table
def make_show_table(show, use_grey_background=False):
    'makes a table for a single radio show'
    cwidths = [.5*inch, .75*inch, 1.25*inch, 3.0*inch, 1.25*inch]
    
    start = "%02d:00" % show.start
    end = "%02d:00" % ((show.start + show.duration) % 24)
        
    hour_range = '%s\nto\n%s' % (start, end)
    header = make_header_table(show)
    
    data = [        
        [hour_range, header, '', '', ''],        
    ]    
    
    tstyles = [
        ('BOX', (0,0), (-1,-1), 2, colors.black),
        ('FONTSIZE', (0,0), (0,0), 13),
        ('TOPPADDING', (0,0), (0,0), -1),        
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (1,0), (2,0), 5),        
        #('BOTTOMPADDING', (1,0), (2,0), 5),            
        ('SPAN', (1,0), (4,0)),
        ('GRID', (0,0), (0,-1), .5, colors.black),
        ('BOX', (1,0), (-1,0), .5, colors.black),                
    ]
    
    is_white = False 
    for hour in range(show.start+1, show.start+show.duration+1):
        hour %= 24 # in case it starts at 23:00 and goes until 01:00 for example
        
        row = len(data)
        psa_or_promo = hour % 2 and 'PSA:' or 'Promo:'
        data.append(
            ["%02d:00" % hour, 'Station ID', 'Certified:', psa_or_promo, 'Certified:']
        )
        tstyles.extend([
            ('ALIGN', (2,row), (4,row), 'LEFT'),
            ('BOX', (1,row), (2,row), .5, colors.black),
            ('BOX', (3,row), (4,row), .5, colors.black),        
        ])
        
    if use_grey_background:            
        tstyles.append(('BACKGROUND', (0, 0), (0, -1), colors.lightgrey))
    
    rheights = [
        None
    ] * len(data)
    
    return Table(data, cwidths, rheights, tstyles)



def make_day_tables(showsAndEvents):    
    '''
    showsAndEvents: a list of show, signon and signoff objects
    returns a list of tables, one table per page. 
    '''
    tables = []
    for i, obj in enumerate(showsAndEvents):
        if isinstance(obj, model.show):            
            tables.append(make_show_table(obj, i%2))
            tables.append(Spacer(0,10))
        if isinstance(obj, model.signon):
            print 'signon'
        if isinstance(obj, model.signoff):
            print 'signoff'
    
    return tables

import model
story=[]
tables = make_day_tables(model.day)
for (i, table) in enumerate(tables):
    story.append(table)
doc = SimpleDocTemplate("prog_table_test.pdf")     
doc.build(story)

#make_day_tables([])
