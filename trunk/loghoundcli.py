#!/usr/bin/python
# -*- coding: UTF-8 -*-

def generateLogs(argv, printcmd, location="./"):
  # FIRST, figure out what days we are going to be printing logs for
  import calendar
  import datetime
  
  calendar.setfirstweekday(calendar.SUNDAY)
  
  if len(argv) < 4:
    printcmd("should be:\n\t%s <year> <month> <day> [number of days]\n" % argv[0])
    return
  
  year  = int(argv[1])
  month = int(argv[2])
  day   = int(argv[3])
  today = datetime.datetime(year,month,day)
  
  numdays = 7
  try:
    numdays = int(argv[4])
  except IndexError:
    pass
  except ValueError:
    pass
  
  if today.weekday() != calendar.SUNDAY:
    printcmd("This is supposed to start on a Sunday.  I assume you know what you're doing.\n")
  
  dates = [today + datetime.timedelta(i) for i in xrange(numdays)]
  progEvents = dict([(date,[]) for date in dates])
  opEvents = dict([(date,[]) for date in dates])
  
  # SECOND, download the schedule
  # TODO: get rid of this and just talk to the database or whatever directly if
  #       that's at all possible!  This is a little silly!  If we're going to
  #       output things this way, we should put out an XML file!
  
  import urllib
  import codecs
  import model
  import json
  
  if True:
    printcmd("Downloading schedule...")
    sched_raw = unicode(urllib.urlopen('http://www.wmbr.org/~lowe/templogs.php?start_year=%d&start_month=%d&start_day=%d&num_days=%d' % (year,month,day,numdays)).read(), "iso-8859-1")
    printcmd("Done.\n")
  else:
    printcmd("Using cached schedule (probably not what you want)...")
    sched_raw = "".join(codecs.open("templogs_sample", "r", "iso-8859-1" ).readlines())
    printcmd("Done.\n")
  
  timestrtodelta = lambda timestr: datetime.timedelta(0, sum(map(lambda x,y: int(x)*y, timestr.split(":"), [60*60,60])))

  printcmd("Adding shows...")
  
  schedule = json.loads(sched_raw)
  for date_str in schedule:
    year  = int(date_str.split("-")[0])
    month = int(date_str.split("-")[1])
    day   = int(date_str.split("-")[2])
    date = datetime.datetime(year,month,day)
    for show in schedule[date_str]:
      if show["type"] == "show":
        progEvents[date].append(model.show(
          show["show_name"],
          date+timestrtodelta(show["start_time"]),
          date+timestrtodelta(show["end_time"]),
          show["engineer"],
          show["producers"],
          show["announcers"]))
      elif show["type"] == "signoff":
        opEvents[date].append((date+timestrtodelta(show["time"]), 'TURN OFF TRANSMITTER'))
        progEvents[date].append(model.signoff(date+timestrtodelta(show["time"])))
      elif show["type"] == "signon":
        opEvents[date].append((date+timestrtodelta(show["time"]), 'TEST EAS LIGHTS AND TURN ON TRANSMITTER'))
        progEvents[date].append(model.signon(date+timestrtodelta(show["time"])))

  printcmd("Done.\n")
  
  # THIRD, compute other events that will occur on a particular day

  printcmd("Inserting FCC events (EAS tests, tower lights)...")
  
  import random
  
  # which dates should have an EAS test?
  easDays = [random.sample(dlist, 1)[0] for dlist in [[d for d in dates[i:i+7] if d.strftime("%A") != "Sunday"] for i in xrange(len(dates)/7)] if len(dlist) > 0]
  
  # check the tower lights at civil twilight
  import twilight
  
  twilights = map(twilight.twilight, dates)
  for date in dates:
    twilightTime = twilight.twilight(date)
    opEvents[date].append((twilightTime, "CHECK TOWER LIGHTS: READING ="))
  
  # random EAS check once per week (taken from last version)
  # EAS tests must be conducted between 8:30 AM and twilight.
  # It is by WMBR convention that they are conducted at half
  # past an hour.  To be conservative, I also bring back the
  # late limit to half-past the previous hour from twilight,
  # thus avoiding any issues involving having the EAS test
  # and twilight too close together.
    if date in easDays:
      easDateTime = date + datetime.timedelta(0, random.randrange(8,twilightTime.hour)*60*60+30*60)
      opEvents[date].append((easDateTime, "CONDUCT REQUIRED WEEKLY EAS TEST"))

  printcmd("Done\n")
  
  # FOURTH, produce the pdf
  
  import os
  from reportlab.platypus import BaseDocTemplate, Frame, NextPageTemplate, PageBreak, PageTemplate, Table, TableStyle, Paragraph, flowables
  from reportlab.lib import colors
  from reportlab.lib.units import inch
  from reportlab.lib.pagesizes import letter
  from reportlab.lib.styles import getSampleStyleSheet
  from reportlab.rl_config import defaultPageSize
  import tablegen
  import progtablegen
  
  #letter paper
  PAGE_WIDTH, PAGE_HEIGHT = letter
  styles=getSampleStyleSheet()
  Elements=[]
  
  def foot(title):
    def _foot(canvas, doc):
      today = datetime.date(doc.docEval("currentYear"), doc.docEval("currentMonth"), doc.docEval("currentDay"))
      canvas.saveState()
      canvas.setFont('Times-Roman',20)
      canvas.drawString(0.3*inch, PAGE_HEIGHT-0.7*inch, title)
      canvas.drawRightString(PAGE_WIDTH-0.5*inch, PAGE_HEIGHT-0.7*inch, today.strftime("%A, %b %d, %Y"))
      # this draws the page number on the outside corner of the log
      if doc.page % 2 == 0:
        canvas.drawString(0.3*inch, 0.3*inch, "Page %d" % (doc.page))
      else:
        canvas.drawRightString(PAGE_WIDTH-0.5*inch, 0.3*inch, "Page %d" % (doc.page))
      canvas.restoreState()
    return _foot
  
  def title(title):
    def _title(canvas,doc):
      canvas.saveState()
      canvas.setFont('Times-Roman',20)
      canvas.drawString(0.3*inch, PAGE_HEIGHT-0.7*inch, title)
      canvas.drawRightString(PAGE_WIDTH-0.5*inch, PAGE_HEIGHT-0.7*inch, "%02d/%02d/%d — %02d/%02d/%d" % (dates[0].month, dates[0].day, dates[0].year, dates[-1].month, dates[-1].day, dates[-1].year))
      canvas.restoreState()
    return _title
  
  def rulesPage(fname = "op_title.xml"):
    eltList = []
    paraPrefix = "<para";
    for elt in "".join(open(fname).readlines()).split(paraPrefix):
      if len(elt.strip()) > 0:
        eltList.append(Paragraph(paraPrefix + elt, styles['Normal']))
    data = [
        ["Henry Holtzman", "Home: 617-327-1298", "Work: 617-253-0319"],
        ["Ted Young",      "Home: 617-776-7473", "Cell: 617-447-8439"] ]
    eltList.append(Table(data, style=[('SIZE',(0,0),(-1,-1),12)]))
    return eltList
  
  def SigPage():
    data = [ ["CUSTODIAN (print name)",
              "INITIALS",
              "TIME ON",
              "SIGNATURE",
              "TIME OFF",
              "SIGNATURE"]
           ] + [[None]*6]*22
    tableWidths = [2*inch,None,None,1.7*inch,None,1.7*inch]
    tableHeights = [None] + [30]*22
    t = Table(data, tableWidths, tableHeights)
    t.setStyle(TableStyle([
          ('VALIGN', (0,0), (-1,0), 'TOP'),
          ('ALIGN', (0,0), (-1,0), 'CENTER'),
          ('ALIGN', (3,0), (3,0), 'RIGHT'),
          ('ALIGN', (5,0), (5,0), 'RIGHT'),
          ('GRID', (0,0), (1,-1), .6, colors.black),
          ('LINEABOVE', (2,0), (3,-1), .6, colors.black),
          ('LINEAFTER', (3,0), (3,-1), .6, colors.black),
          ('LINEABOVE', (4,0), (5,-1), .6, colors.black),
          ('LINEAFTER', (5,0), (5,-1), .6, colors.black),
          ('BOX',(0,0),(-1,-1),2,colors.black),
          ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
          ('VALIGN', (0,1), (0, -1), 'MIDDLE'),
      ]))
    return t
  
  ## The operating log
  
  printcmd("Writing operating log...")

  doc = BaseDocTemplate(location+"oplog.pdf",showBoundary=0,allowSplitting=0,leftMargin=0.5*inch,rightMargin=0.5*inch,topMargin=1.4*inch,bottomMargin=0.5*inch)
  
  frameNormal = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
  
  Elements.extend(rulesPage())
  
  for date in dates:
    Elements.append(flowables.DocAssign("currentYear",  date.year))
    Elements.append(flowables.DocAssign("currentMonth", date.month))
    Elements.append(flowables.DocAssign("currentDay",   date.day))
    tables = tablegen.make_day_tables(opEvents[date])
    Elements.append(NextPageTemplate('OTALogPage'))
    Elements.append(PageBreak())
    Elements.append(SigPage())
    for table in tables:
      Elements.append(NextPageTemplate('OpLogPage'))
      Elements.append(PageBreak())
      Elements.append(table)
  
  doc.addPageTemplates([PageTemplate(id='Title',frames=frameNormal,onPage=title("WMBR Operating Log"),pagesize=letter),
                        PageTemplate(id='OTALogPage',frames=frameNormal,onPage=foot("WMBR Operating Log"),pagesize=letter),
                        PageTemplate(id='OpLogPage',frames=frameNormal,onPage=foot("WMBR Operating Log"),pagesize=letter)
                        ])
  
  #start the construction of the pdf
  doc.build(Elements)

  printcmd("Done\n")
  
  ## The programming log
  
  printcmd("Writing programming log...")
  doc = BaseDocTemplate(location+"proglog.pdf",showBoundary=0,allowSplitting=0,leftMargin=0.5*inch,rightMargin=0.5*inch,topMargin=1.4*inch,bottomMargin=0.5*inch)
  
  frameNormal = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
  
  Elements.extend(rulesPage())
  
  for date in dates:
    Elements.append(flowables.DocAssign("currentYear",  date.year))
    Elements.append(flowables.DocAssign("currentMonth", date.month))
    Elements.append(flowables.DocAssign("currentDay",   date.day))
    tables = progtablegen.make_day_tables(progEvents[date])
    Elements.append(NextPageTemplate('OTALogPage'))
    Elements.append(PageBreak())
    Elements.append(SigPage())
    Elements.append(NextPageTemplate('ProgLogPage'))
    Elements.append(PageBreak())
    Elements.extend(tables)
  
  doc.addPageTemplates([PageTemplate(id='Title',frames=frameNormal,onPage=title("WMBR Programming Log"),pagesize=letter),
                        PageTemplate(id='OTALogPage',frames=frameNormal,onPage=foot("WMBR Programming Log"),pagesize=letter),
                        PageTemplate(id='ProgLogPage',frames=frameNormal,onPage=foot("WMBR Programming Log"),pagesize=letter)
                        ])
  
  #start the construction of the pdf
  doc.build(Elements)
  printcmd("Done\n")
  printcmd("Finished.\n")

if __name__ == '__main__':
  import sys
  def printcmd(x):
    sys.stderr.write(x)
    sys.stderr.flush()
  generateLogs(sys.argv, printcmd)
