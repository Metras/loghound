"""
tablegen generates WMBR's operations tables. It consists of one function:
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
    '\n\nCHAN: MIN: NOM: MAX: UNITS:'.replace(' ', '\n'),
    'FWD. POWER 3 90 100 105 %'.replace(' ', '\n'),
    'RFL. POWER 4 0 0 10 %'.replace(' ', '\n'),
    'ROOM TEMP 6 50 75 95 F'.replace(' ', '\n'),
    NOTES, # to enforce consistency between this and the next statement
    'Time\nChecked',
    'Checked\nBy'
]
NOTES_IDX = HEADER_ROW.index(NOTES)
NUM_COLS = len(HEADER_ROW) 

# reportlab uses 'None' in this context to mean: autofit
HEADER_ROW_HEIGHT = None
HOUR_ROW_HEIGHT = 40
EVENT_ROW_HEIGHT = 15
NOTES_COL_WIDTH = 4*inch
COL_WIDTHS = \
    [None]*NOTES_IDX + [NOTES_COL_WIDTH] + [None]*(NUM_COLS - NOTES_IDX - 1)
EVENT_COL_SPAN = 4

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
def make_day_tables(events):
    """
    Given a sequence of a day's events, tablegen returns a list of two Table
    objects that, taken together, represent operations for that day. 
    
    It returns two tables because each one takes up a full page.  
    
    Usage: 
    
    # consider a day with three events: turn off transmitter at 3:05am, 
    # test EAS at 5:45, and check tower lights at 6:17pm. to generate 
    # the day's operating table: 
    >>> make_day_tables([
    ... (datetime(2009, 10, 28, 3, 5),  'TURN OFF TRANSMITTER'),
    ... (datetime(2009, 10, 28, 5, 45), 'TEST EAS LIGHTS'),
    ... (datetime(2009, 10, 28, 18,17), 'CHECK TOWER LIGHTS: READING =')     
    ... ])            
    [<Table>, <Table>]     
    """
    
    # adds a row for one of the normal hours in the table:
    # all blank cells except the first.     
    def add_hour_row(hour, rows, row_heights):
        row = ['%d:00' % hour] + [''] * (NUM_COLS - 1)
        rows.append(row)
        row_heights.append(HOUR_ROW_HEIGHT)
    
    # adds a special event 
    # the event text takes up a span
    def add_event_row(display_time, text, rows, row_heights, styles):
        row = [display_time, text] + ['']*(NUM_COLS - 2)
        row_idx = len(rows)
        rows.append(row)
        row_heights.append(EVENT_ROW_HEIGHT)
        styles.extend([
            # special events take up multiple columns
            ('SPAN', (1,row_idx), (EVENT_COL_SPAN,row_idx)), 
            # need to fiddle with padding to make narrow rows look good 
            ('TOPPADDING', (0,row_idx), (-1,row_idx), 0),
            ('BOTTOMPADDING', (1,row_idx), (-1,row_idx), 2.5)
        ])
        
    def make_table(events, hours):
        # add to these as rows are added
        rows = [HEADER_ROW] 
        row_heights = [HEADER_ROW_HEIGHT] 
        styles = list(TABLE_BASE_STYLE)
        # start adding...
        for hour in hours:
            add_hour_row(hour, rows, row_heights)
            for event in events:
                dt, text = event # dt is a datetime object
                if hour == dt.hour:
                    # minor nitpic: dt.strftime forces zero padding. 
                    # use regular ol' sprintf instead
                    display_time = "%d:%02d" % (dt.hour, dt.minute) 
                    add_event_row(display_time,text,rows,row_heights,styles) 
                            
        table = Table(rows, COL_WIDTHS, row_heights)
        table.setStyle(styles)
        return table
    
    table1 = make_table(events, range(12))
    table2 = make_table(events, range(12, 24))
    
    return (table1, table2)

########### standalone smoketest    
def main():
    '''
    run as a standalone, tablegen produces a fixed mockup named  
    operating_table_mockup.pdf        
    
    this mockup illustrates all the corner cases that events can fall into:
    events that start on the hour, multiple events within the same hour, 
    multiple events occuring at the same time, and events at the first and 
    last minute of the day. 
    '''
    
    doc = SimpleDocTemplate("operating_table_mockup.pdf")     
    story = [] 
    story.extend(make_day_tables([
        (datetime(2009, 10, 28, 0, 0),   'DROP THE JAZZ, GRATEFUL DEAD'),        
        (datetime(2009, 10, 28, 3, 5),   'TURN OFF TRANSMITTER'),
        (datetime(2009, 10, 28, 5, 45),  
            'TEST EAS LIGHTS AND TURN ON TRANSMITTER'),
        (datetime(2009, 10, 28, 11, 45), 'MY ASS IS ON FIRE'),
        (datetime(2009, 10, 28, 12, 00), 'TEST YOUR MOM'),
        (datetime(2009, 10, 28, 12, 59), 
            'WINNERS ARE LOSERS WITH A NEW ATTITUDE'),
        (datetime(2009, 10, 28, 12, 59), 'ROCK WITH IT'),                 
        (datetime(2009, 10, 28, 13, 00), 'STOP PLAYING METALLICA, FOOL'),
        (datetime(2009, 10, 28, 18,17),  'CHECK TOWER LIGHTS: READING ='),
        (datetime(2009, 10, 28, 23, 01), 'ENABLE HUMPBACK WHALES II'),
    ]))
    story.insert(1, PageBreak())
    
    doc.build(story)
    
if __name__ == '__main__':
    main()
