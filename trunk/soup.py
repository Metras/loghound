#!/usr/bin/python
# -*- coding: UTF-8 -*-

# FIRST, figure out what days we are going to be printing logs for
import calendar
import sys
import datetime

calendar.setfirstweekday(calendar.SUNDAY)

if len(sys.argv) < 4:
  print "should be:\n\t%s <year> <month> <day>" % sys.argv[0]
  sys.exit(0)

year  = int(sys.argv[1])
month = int(sys.argv[2])
day   = int(sys.argv[3])
today = datetime.date(year,month,day)
print "year  = %4d"      %   year
print "month = %4d = %s" % (month, calendar.month_name[month])
print "day   = %4d = %s" % (  day, calendar.day_name[calendar.weekday(year,month,day)])

if today.weekday() != calendar.SUNDAY:
  print "This is supposed to start on a Sunday.  I assume you know what you're doing."

dates = [today + datetime.timedelta(i) for i in xrange(7)]
for date in dates:
  print date

# SECOND, download the schedule
# TODO: get rid of this and just talk to the database or whatever directly if
#       that's at all possible!  This is a little silly!  If we're going to
#       output things this way, we should put out an XML file!

import urllib

sched_raw = urllib.urlopen('http://wmbr.org/cgi-bin/prog_log_input').read()

# remove /* comments */
while sched_raw.find("/*") > -1:
  sidx = sched_raw       .find("/*")
  eidx = sched_raw[sidx:].find("*/")
  if eidx == -1:
    break
  eidx += sidx + 2
  sched_raw = sched_raw[:sidx] + sched_raw[eidx:]

sched_raw = ("".join(sched_raw.split("\\"))).split('\n')

schedule = {}
lidx = 0
while lidx < len(sched_raw):
  line = sched_raw[lidx]
  if line in ['Sunday:', 'Monday:', 'Tuesday:', 'Wednesday:', 'Thursday:', 'Friday:', 'Saturday:']:
    day = line[:-1]
    schedule[day] = []
  elif line[3:13] == "first_show":
    schedule[day].append(("first_show", line[14:]))
  elif line[3: 7] == "show":
    args = line[3:].split("   ")
    schedule[day].append(("show", args[1], args[2][2:-1].split('","')))
  elif line[3:10] == "signoff":
    schedule[day].append(("signoff",))
  elif line[3: 9] == "signon":
    schedule[day].append(("signon", line[9:].strip()))
  elif line       == "end":
    pass
  elif line[ : 9] == "alt_shows":
    schedule[day].append(("alt_show", line[9:19].strip(), sched_raw[lidx][19:-1].split('","'), sched_raw[lidx+1][19:-1].split('","')))
    lidx += 1
  elif len(line.strip()) == 0:
    pass # we don't need no empty lines
  else:
    print "?? '%s'" % line
  lidx += 1

for i in schedule.keys():
  print i
  for j in schedule[i]:
    print "", j

# THIRD, compute other events that will occur on a particular day

import twilight

twilights = map(twilight.twilight, dates)

# FOURTH, produce the pdf

import os
from reportlab.platypus import BaseDocTemplate, Frame, Paragraph, NextPageTemplate, PageBreak, PageTemplate, Table, TableStyle
from reportlab.platypus import flowables
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize

#letter paper
PAGE_WIDTH=8.5*inch
PAGE_HEIGHT=11.5*inch
letter=[PAGE_WIDTH,PAGE_HEIGHT]
styles=getSampleStyleSheet()
Elements=[]

doc = BaseDocTemplate("basedoc.pdf",showBoundary=0,allowSplitting=0,leftMargin=0.5*inch,rightMargin=0.5*inch)

def foot(canvas,doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',19)
    canvas.drawString(inch, 0.75 * inch, "WMBR Operating Log")
    canvas.drawRightString(PAGE_WIDTH-1.25*inch, 0.75*inch, "%02d/%02d/%d" % (doc.docEval("currentMonth"), doc.docEval("currentDay"), doc.docEval("currentYear")))
    canvas.restoreState()

def title(canvas,doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',20)
    canvas.drawString(0.5*inch, PAGE_HEIGHT-0.5*inch, "WMBR Operating Log")
    canvas.drawRightString(PAGE_WIDTH-0.75*inch, PAGE_HEIGHT-0.5*inch, "%02d/%02d/%d — %02d/%02d/%d" % (dates[0].month, dates[0].day, dates[0].year, dates[-1].month, dates[-1].day, dates[-1].year))
    canvas.restoreState()

#normal frame as for SimpleFlowDocument
frameRules = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')

#normal frame as for SimpleFlowDocument
frameT = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')

Elements.append(Paragraph("""
<para alignment=CENTER spaceBefore=24 spaceAfter=12 fontSize=12><b>WMBR</b> is a registered service mark of the Technology Broadcasting Corporation.</para>
""", styles['Normal']))
Elements.append(Paragraph("""
<para alignment=CENTER spaceBefore=40 spaceAfter=12 fontSize=18>“RULES OF THE LOGS”</para>
""", styles['Normal']))
Elements.append(Paragraph("""
<para alignment=CENTER fontSize=12>Questions on these rules should be referred to the Chief Engineer.</para>
""", styles['Normal']))
# rules
for para in open("op_title.xml"):
  Elements.append(Paragraph(
    "<para bulletIndent=10 leading=12 leftIndent=25 spaceBefore=6 spaceAfter=12 rightIndent=10 fontSize=12><bullet><seq id='rulenum'/>.</bullet>%s</para>" % para,
    styles['Normal']))
Elements.append(Paragraph("""
<para alignment=CENTER spaceBefore=24 spaceAfter=12 fontSize=15>The Emergency Technical Staff:</para>
""", styles['Normal']))
data = [
    ["Henry Holtzman", "Home: 617-327-1298", "Work: 617-253-0319"],
    ["Ted Young",      "Home: 617-776-7473", "Cell: 617-447-8439"] ]
Elements.append(Table(data, style=[('SIZE',(0,0),(-1,-1),12)]))

def SigPage():
  data = [ ["CUSTODIAN (print name)",
            "INITIALS",
            "TIME ON",
            "SIGNATURE",
            "TIME OFF",
            "SIGNATURE"]
         ] + [[" "]*6]*22
  tableWidths = [2*inch,None,None,1.7*inch,None,1.7*inch]
  tableHeights = [None] + [30]*22
  t = Table(data, tableWidths, tableHeights)
  t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,0), 'TOP'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('GRID', (0,0), (1,-1), .6, colors.black),
        ('LINEABOVE', (2,0), (3,-1), .6, colors.black),
        ('LINEAFTER', (3,0), (3,-1), .6, colors.black),
        ('LINEABOVE', (4,0), (5,-1), .6, colors.black),
        ('LINEAFTER', (5,0), (5,-1), .6, colors.black),
        ('BOX',(0,0),(-1,-1),2,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('ALIGN', (0,1), (0, -1), 'CENTER'),
        ('VALIGN', (0,1), (0, -1), 'MIDDLE'),
    ]))
  return t


for date in dates:
  Elements.append(flowables.DocAssign("currentYear",  date.year))
  Elements.append(flowables.DocAssign("currentMonth", date.month))
  Elements.append(flowables.DocAssign("currentDay",   date.day))
  Elements.append(NextPageTemplate('OTALogPage'))
  Elements.append(PageBreak())
  Elements.append(SigPage())
  Elements.append(NextPageTemplate('OpLogPage'))
  Elements.append(PageBreak())
  Elements.append(Paragraph("Moustaches", styles['Normal']))

doc.addPageTemplates([PageTemplate(id='Title',frames=frameRules,onPage=title,pagesize=letter),
                      PageTemplate(id='OTALogPage',frames=frameT,onPage=foot,pagesize=letter),
                      PageTemplate(id='OpLogPage',frames=frameT,onPage=foot,pagesize=letter)
                      ])

#start the construction of the pdf
doc.build(Elements)
