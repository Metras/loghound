#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
progtablegen generates WMBR's programming tables. It consists of one function:
make_day_tables
"""

import datetime, model

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

# TODO

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
    cwidths = [.5*inch, .75*inch, 1.25*inch, 3.8*inch, 1.25*inch]
    
    start = show.start.strftime("%H:%M")
    end = (show.start+show.duration).strftime("%H:%M")
        
    hour_range = "%s\n–\n%s" % (start, end)
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
        ('LEFTPADDING', (1,0), (2,0), 0),           
        #('BOTTOMPADDING', (1,0), (2,0), 5),            
        ('SPAN', (1,0), (4,0)),
        ('GRID', (0,0), (0,-1), .5, colors.black),
        ('BOX', (1,0), (-1,0), .5, colors.black),                
    ]
    

    # was: 
    # for hour in range(show.start.hour, (show.start+show.duration+datetime.timedelta(0,59*60)).hour):
    start_hour = show.start.hour
    end_hour = (show.start + show.duration).hour
    if (end_hour < 12) and (start_hour > 12):
         end_hour += 24
    for hour in range(start_hour+1, end_hour+1):
        hour %= 24 # in case it starts at 23:00 and goes until 01:00 for example
        
        row = len(data)
        # if hour == (show.start+show.duration).hour and (show.start+show.duration).minute != 0:
        #   pass
        if False:
            pass
        else:
          psa_or_promo = hour % 2 and 'PSA:' or 'Promo:'
          data.append(
              ["%02d:00" % (hour), 'Station ID', '➤'+'_'*15, psa_or_promo, '➤'+'_'*14]
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

def make_sign_table(time, is_signon):
    if  is_signon:
        label = 'Station Sign-On'
    else:
        label = 'Station Sign-Off'
    
    para = Paragraph('<b>%s</b>' % label, styles['Normal'])
    
    data = [["%02d:%02d" % (time.hour, time.minute), label, '➤'+'_'*14]]
    cwidths = [.5*inch, 3*inch, 4.05*inch]
    rheights = [None]
    tstyles = [
           ('BOX', (0,0), (-1,-1), 2, colors.black),
           ('ALIGN', (0,0), (0,0), 'CENTER'),
           ('ALIGN', (1,0), (1,0), 'LEFT'),
           ('ALIGN', (-1,0), (-1,0), 'RIGHT'),           
           ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
           ('GRID', (0,0), (0,-1), .5, colors.black),
           #('BOX', (1,0), (-1,0), .5, colors.black),                
    ]
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
        if isinstance(obj, model.signon):
            tables.append(make_sign_table(obj.time, True))            
        if isinstance(obj, model.signoff):
            tables.append(make_sign_table(obj.time, False))            
        tables.append(Spacer(0,10))
    
    return tables

if __name__ == "__main__":
  story=[]
  tables = make_day_tables(model.day)
  for (i, table) in enumerate(tables):
      story.append(table)
  doc = SimpleDocTemplate("prog_table_test.pdf")
  doc.build(story)

#make_day_tables([])
