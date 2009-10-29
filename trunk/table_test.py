# disgusting code dan is using to explore reportlab tables

import reportlab
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet 
from reportlab.lib.units import inch 
PAGE_HEIGHT, PAGE_WIDTH = reportlab.lib.pagesizes.letter

styles = getSampleStyleSheet() 

Title = "Hello world" 
pageinfo = "platypus example" 
def myFirstPage(canvas, doc): 
    canvas.saveState() 
    canvas.setFont('Times-Bold',16) 
    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title) 
    canvas.setFont('Times-Roman',9) 
    canvas.drawString(inch, 0.75 * inch, "First Page / %s" % pageinfo) 
    canvas.restoreState() 


def myLaterPages(canvas, doc): 
    canvas.saveState() 
    canvas.setFont('Times-Roman',9) 
    canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo)) 
    canvas.restoreState() 

doc = SimpleDocTemplate("phello.pdf") 
story = [] 
style = styles["Normal"] 

data = [
    ['\n\nCHAN: MIN: NOM: MAX: UNITS:'.replace(' ', '\n'),
     'FWD. POWER 3 90 100 105 %'.replace(' ', '\n'),
     'RFL. POWER 4 0 0 10 %'.replace(' ', '\n'),
     'ROOM TEMP 6 50 75 95 F'.replace(' ', '\n'),
     'NOTES',
     'Time\nChecked',
     'Checked\nBy'
    ],
]

data += [  ['%d:00' % d] + [' ']*6 for d in range(0,3)  ]

data += [['3:05', 'TURN OFF TRANSMITTER'] + ['']*5]

data += [  ['%d:00' % d] + [' ']*6 for d in range(4,6)  ]

data += [['5:45', 'TEST EAS LIGHTS AND TURN ON TRANSMITTER'] + ['']*5]

data += [  ['%d:00' % d] + [' ']*6 for d in range(6,12)  ]

tableWidths = [None]*4+[4*inch]+[None]*2
tableHeights = [None] + [50]*(3) + [15] + [50]*2 + [15] + [50]*6
t=Table(data, tableWidths, tableHeights) 
t.setStyle(TableStyle(
    [
        ('VALIGN', (0,0), (-1,0), 'TOP'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('GRID', (0,0), (-1,-1), .6, colors.black),
        ('BOX',(0,0),(-1,-1),2,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('ALIGN', (0,1), (0, -1), 'CENTER'),
        ('VALIGN', (0,1), (0, -1), 'MIDDLE'),
        
        ('SPAN',(1,4),(-3,4)),
        ('TOPPADDING', (0,4), (-1,4), 0),
        ('BOTTOMPADDING', (1,4), (-1,4), 2.5),                
        
        ('SPAN',(1,7),(-3,7)),
        ('TOPPADDING', (0,7), (-1,7), 0),
        ('BOTTOMPADDING', (1,7), (-1,7), 2.5),                
        
    ])) 
    
story.append(t)
#doc.build(story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
doc.build(story)
