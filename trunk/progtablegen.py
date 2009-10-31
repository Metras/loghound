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
