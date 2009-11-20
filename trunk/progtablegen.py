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
def make_show_table(show, use_grey_background=False, include_signon=False, include_signoff=False):
    'makes a table for a single radio show'
    cwidths = [.5*inch, .75*inch, 1.25*inch, 3.8*inch, 1.25*inch]
    
    start = show.start.strftime("%H:%M")
    end   = show.end  .strftime("%H:%M")
        
    hour_range = "%s\n–\n%s" % (start, end)
    header = make_header_table(show)
    
    data = [
        [hour_range, header, '', '', ''], 
    ]    
    
    tstyles = [
        ('BOX', (0,0), (-1,-1), 3, colors.black),
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
    
    start_hour = show.start.hour
    end_hour   = show.end  .hour
    if (end_hour < 12) and (start_hour > 12):
         end_hour += 24
             
    if include_signon:
        row, new_styles = make_signon_row(show.start, row=len(data))
        data.append(row)
        tstyles.extend(new_styles)        
    
    for hour in range(start_hour+1, end_hour+1):
        hour %= 24 # in case it starts at 23:00 and goes until 01:00 for example
        row = len(data)
        if False:
            pass
        else:
          psa_or_promo = (hour % 2 == 0) and 'PSA:' or 'Promo:'
          data.append(
              ["%02d:00" % (hour), 'Station ID', '➤'+'_'*15, psa_or_promo, '➤'+'_'*14]
          )
          tstyles.extend([
              ('ALIGN', (2,row), (4,row), 'LEFT'),
              ('BOX', (1,row), (2,row), .5, colors.black),
              ('BOX', (3,row), (4,row), .5, colors.black),
          ])
    
    if include_signoff:
        row, new_styles = make_signoff_row(show.end, row=len(data))        
        data.append(row)
        tstyles.extend(new_styles)        
        
    if use_grey_background:            
        tstyles.append(('BACKGROUND', (0, 0), (0, -1), colors.lightgrey))
    
    rheights = [
        None
    ] * len(data)
    
    return Table(data, cwidths, rheights, tstyles)

def make_signon_row(time, row):
    return make_signinoff_row(time, row, True)    
def make_signoff_row(time, row):    
    return make_signinoff_row(time, row, False)    
def make_signinoff_row(time, row, is_signon):
    if  is_signon:
        label = 'Station Sign-On'
    else:
        label = 'Station Sign-Off'
    
    para = Paragraph('<b>%s</b>' % label, styles['Normal'])
    
    data_row = ["%02d:%02d" % (time.hour, time.minute), label, '', '➤'+'_'*14, '']
    tstyles = [
           ('ALIGN', (0,row), (0,row), 'CENTER'),
           ('ALIGN', (1,row), (1,row), 'LEFT'),
           ('ALIGN', (3,row), (3,row), 'RIGHT'),           
           # ('GRID', (0,row), (-1,row), .5, colors.black),
           # ('LINEAFTER', (2, row), (2, row), 1, colors.white),
           # ('LINEABOVE', (2, row), (3, row), 1, colors.black),                      
           ('SPAN', (1,row), (2,row)),
           ('SPAN', (3, row), (4, row)),
           # ('BOX', (1,0), (-1,0), .5, colors.black),                
    ]
    return data_row, tstyles

def trigrams(seq, pad_left=False, pad_right=False):
    '''
    get trigrams: 
    
    >>> trigrams([1,2,3,4,5])
    [(1,2,3), (2,3,4), (3,4,5)]
    '''
    if pad_left:
        seq = [None]*pad_left + seq
    if pad_right:
        seq = seq + [None]*pad_right
    count = max(0, len(seq) - 2)
    return [tuple(seq[i:i+3]) for i in range(count)]

def make_day_tables(showsAndEvents):    
    '''
    showsAndEvents: a list of show, signon and signoff objects
    returns a list of tables, one table per page. 
    '''
    tables = []
    for i, trigram in enumerate(trigrams(showsAndEvents, pad_left=1, pad_right=1)):
        
        previous, event, next = trigram
        
        if isinstance(event, model.show):
            show = event
            kwargs = {}
            if isinstance(previous, model.signon):
                kwargs['include_signon'] = True
            if isinstance(next, model.signoff):
                kwargs['include_signoff'] = True
            tables.append(make_show_table(show, i%2, **kwargs))
        
        # if isinstance(obj, model.show):            
        #     tables.append(make_show_table(obj, i%2))
        # if isinstance(obj, model.signon):
        #     tables.append(make_sign_table(obj.time, True))            
        # if isinstance(obj, model.signoff):
        #     tables.append(make_sign_table(obj.time, False))            
        #tables.append(Spacer(0,1))
    
    return tables

if __name__ == "__main__":
  story=[]
  tables = make_day_tables(model.day)
  for (i, table) in enumerate(tables):
      story.append(table)
  doc = SimpleDocTemplate("prog_table_test.pdf")
  doc.build(story)

#make_day_tables([])
