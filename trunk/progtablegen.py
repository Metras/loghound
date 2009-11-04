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

class show:
    def __init__(self, name, start, end, engineer, producer, announcer):
        self.name = name
        self.start = start
        self.end = end
        self.engineer = engineer
        self.producer = producer
        self.announcer = announcer
        
class signon:
    def __init__(self, time):        
        self.time = time
        
class signoff:
    def __init__(self, time):
        self.time = time

styles=getSampleStyleSheet() 

def make_day_tables(showsAndEvents):    
    '''
    showsAndEvents: a list of show, signon and signoff objects
    returns a list of tables, one table per page. 
    '''
    cwidths = [1*inch]+[3*inch, 3*inch]
    rheights= [40]*22
    
    

    return make_header_table(show2)
    



def make_show_table(show, ):
    data = [
        ['00:00\nto\n01:00', make_header_table(show), '', '', ''],        
        ['01:00', 'Station Id', 'Certified:', 'Promo:', 'Certified:']
    ]
    
    cwidths = [.5*inch, .75*inch, 1.25*inch, 3.0*inch, 1.25*inch]
    
    rheights = [
        None
    ] * 2
    
    tstyles = [
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (1,0), (2,0), 5),        
        #('BOTTOMPADDING', (1,0), (2,0), 5),        
        ('SPAN', (1,0), (4,0)),
        ('ALIGN', (2,1), (4,1), 'LEFT'),
        ('GRID', (0,0), (0,-1), .5, colors.black),
        ('BOX', (1,1), (2,1), .5, colors.black),
        ('BOX', (3,1), (4,1), .5, colors.black),        
        ('BOX', (1,0), (-1,0), .5, colors.black),
    ]
    
    return Table(data, cwidths, rheights, tstyles)

def make_header_table(show):
    # nested table: has show name + producer/announcer/engineer 
    # order: 
    #   show name,  engineer
    #   producer
    #   announcer
        
    # note: tried using canvas.stringWidth(), 
    # and two paragraph internal methods: paragraph.minWidth(), 
    # and [sic] paragraph.getActualLineWidths0()
    #
    # none of these gave good numbers on how wide 
    # a paragraph is. i'm therefore going to refrain from
    # trying to manually set the column widths.
    #
    # instead it'll work like this: 
    # 1. give a huge column width for the show title, 
    # because show titles will often be long. 
    #
    # 2. give a small width for the engineer field, 
    # that will accomodate a single longish name. 
    # if the name is too many characters, default
    # to a blank engineer field. long engineer names
    # are a small corner case, no reason to make a big
    # deal out of it. 
    

    if len(show.name) >= 55:
        # issue warning
        print 'warning: this show name might be too long: '+show.name
              
    def cutIfLong(s, chars):
        # if something is too big to fit in the table,
        # return an empty string instead. 
        #
        # note: it'd be better to use the actual rendering
        # size than the character length. see note above:
        # i couldn't get it working for paragraphs. 
        if len(s) > chars:
            print "cutting this string because it's too long: "+s
            return ''
        else:
            return s
        
    def para(label, value, align='left'):
        if not value.strip():
            value = ''       
            extra_attrs = 'rindent="100"' 
        else:
            extra_attrs = ''
        text = '<para align=%s %s><b>%s:</b> %s</para>' % (align, extra_attrs, label, value)        
        return Paragraph(text, styles['Normal'])                 
    
    def show_para(show):
        return Paragraph('<para size="12"><b><i>%s</i></b></para>' % show, styles['Normal'])
        
    # get plurals right
    producer_label = ',' in show.producer and 'Producers' or 'Producer'
    announcer_label = ',' in show.announcer and 'Announcers' or 'Announcer'
        
    data = [
        [show_para(show.name), para('Engineer', cutIfLong(show.engineer, 20), align='right')],            
        [para(producer_label, cutIfLong(show.producer, 60)), ''],
        [para(announcer_label, cutIfLong(show.announcer, 60)), '']
    ]
    
    tstyles = [
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),            
        ('BOTTOMPADDING', (0,0), (-1,0), 2),                    
        ('TOPPADDING', (0,0), (-1,0), 3.5),                    
        
        #('GRID', (0,0), (-1,-1), .6, colors.black),            
        ('BORDER', (0,0), (-1,-1), .6, colors.black),                    
        ('SPAN', (0,1), (1,1)), 
        ('SPAN', (0,2), (1,2)),             
    ]
    
    cwidths = [4*inch, None]
    #rheights = [None, .2*inch, .2*inch]
    rheights = [None, None, None]
    return Table(data, cwidths, rheights, tstyles)






###### test shows

# baseline
show1 = show('Music for Human Beings', 
            '17:00', '19:00', 
            'Dr. Jalis As-Sakran', 
            'Lester Woods', 
            'Peace Child Peter')

# no engineer, announcer or producer
show2 = show("Generoso's Bovine Ska and Polka and Rocksteady", 
            '19:00', '20:00', 
            '', 
            '', 
            '')

# long engineer name
show3 = show('Jazz Train', 
            '20:00', '21:00', 
            'Dr. Jalis "Doctor" As-Sakran Jr.', 
            'Lester Woods, Pat Greenleaf',
            'Peace Child Peter, Prof Levine')

# long producer and announcer name
show4 = show("Terrashow", 
            '21:00', '22:00', 
            'Peace Child Peter',
            'Adam Bockelie, Ka Man Chan, Tracey Hayse, Elizabeth Jones, Yusung Lim, Emily Moberg', 
            'Tracey Hayse, Adam Bockelie, Elizabeth Jones, Ka Man Chan, Yusung Lim, Emily Moberg')
    
# long show name
show5 = show("Generoso's Bovine Ska and Polka and Rocksteady Show", 
            '22:00', '23:00', 
            'Gene', 
            'Gene', 
            'Gene')

# long show, engineer, producer and announcer name
show6 = show("Generoso's Bovine Ska and Polka and Rocksteady Show II", 
            '23:00', '00:00', 
            'Generoso "Sweet Victory" Fierro', 
            'Adam Bockelie, Ka Man Chan, Tracey Hayse, Elizabeth Jones, Yusung Lim, Emily Moberg', 
            'Adam Bockelie, Ka Man Chan, Tracey Hayse, Elizabeth Jones, Yusung Lim, Emily Moberg')
    

shows = [show1, show2, show3, show4, show5, show6]







story=[]
story.append(make_show_table(show5))
doc = SimpleDocTemplate("prog_table_test.pdf")     
doc.build(story)

#make_day_tables([])
