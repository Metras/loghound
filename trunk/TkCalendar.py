#!/usr/bin/env python

'''
    Description:    a calendar-widget for Tkinter
    Version:        0.2
    Copyright:      2004 by Markus Weihs (ehm_dot_weihs_at_utanet_dot_at)
    Created:        2004-07-17
    Last modified:  2010-01-31 (by alawi)
    Licence:        free
    Requirements:   Python,Tkinter
'''

import Tkinter as tk
from calendar import setfirstweekday, monthcalendar, monthrange, month_abbr

class TkCalendar(tk.Frame):
    def __init__(self,parent,y,m,d):
        tk.Frame.__init__(self,parent,bd=2,relief=tk.GROOVE)
        self.year = y
        self.month = m
        self.chosenrow = (d - 1 + ((monthrange(y,m)[0] + 1) % 7))/7

        self.dayArray = ["Su","Mo","Tu","We","Th","Fr","Sa"]
        setfirstweekday(6)

        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Button(f,
            text='<',
            command=self.__decrease,
            relief=tk.FLAT).pack(side=tk.LEFT)
        self.l = tk.Label(f)
        self.l.pack(side=tk.LEFT,expand="yes",fill='x')
	self.__redrawlabel()
        tk.Button(f,
            text='>',
            command=self.__increase,
            relief=tk.FLAT).pack(side=tk.RIGHT)

        self.c = tk.Canvas(self,
            width=155,height=135,
            bg='white',bd=2,relief=tk.GROOVE)
        self.c.bind('<1>', self.__click)
        self.c.pack()
       
        self.__fill_canvas()
        self.__setchosen(self.chosenrow)

    def __fill_canvas(self):
        m = monthcalendar(self.year,self.month)
        for row in range(len(m)):
          rowtext = " ".join(["%2d" % m[row][col] if m[row][col] > 0 else "  " for col in range(len(m[0])) ])
          px, py = self.__pixel(0, row)
          pyn = self.__pixel(0, row-0.5)[1]
          pyx = self.__pixel(0, row+0.5)[1]
          self.c.create_rectangle(px, pyn, px+155, pyx, fill='white', width=0, tags='week%d'%row)
          self.c.create_text(px, py, text=rowtext, anchor="w", font=('Courier',15), tags='day%d'%row)
        px,py = self.__pixel(0,-1)
        self.c.create_text(px, py, text=" ".join(self.dayArray), anchor="w", fill='blue', font=('Courier', 15), tags='header')

    def __pixel(self,col,row):
      return col*20+5,row*20+30

    def __clear(self):
      self.__unchoose()
      self.c.delete('day')
      for i in xrange(10):
        self.c.delete('day%d' % i)
        self.c.delete('week%d' % i)

    def __redrawlabel(self):
        self.l.configure(text="%s %i" % (month_abbr[self.month], self.year))

    def __decrease(self):
        self.__clear()
        if self.month == 1:
            self.year -= 1
            self.month = 12
        else:
            self.month -= 1
	self.__redrawlabel()
        self.__fill_canvas()
   
    def __increase(self):
        self.__clear()
        if self.month == 12:
            self.year += 1
            self.month = 1
        else:
            self.month += 1
	self.__redrawlabel()
        self.__fill_canvas()
   
    def __click(self,event):
        x = self.c.find_closest(event.x,event.y)[0]
        tags = self.c.itemcget(x,'tags')
        if tags.find("day") >= 0:
          tidx = tags.find("day")
          self.__setchosen(int(tags[tidx+3:tidx+5]))
        elif tags.find("week") >= 0:
          tidx = tags.find("week")
          self.__setchosen(int(tags[tidx+4:tidx+6]))

    def __setchosen(self,row):
      self.__unchoose()
      self.chosenrow = row
      self.c.itemconfigure("day%d"%self.chosenrow, fill='red')
      self.c.itemconfigure("week%d"%self.chosenrow, fill='yellow')

    def __unchoose(self):
      if self.chosenrow != None:
        self.c.itemconfigure("day%d"%self.chosenrow, fill='black')
        self.c.itemconfigure("week%d"%self.chosenrow, fill='white')
        self.chosenrow = None

    def chosenDay(self):
      if self.chosenrow is None:
	return None
      import datetime
      x = datetime.datetime(self.year,self.month,1)
      x += datetime.timedelta(self.chosenrow * 7)
      x -= datetime.timedelta((monthrange(self.year,self.month)[0] + 1) % 7)
      return x.year, x.month, x.day

if __name__ == '__main__':
    from time import localtime
    year,month,day = localtime()[0:3]
    root = tk.Tk()
    c = TkCalendar(root, year, month, day)
    c.pack()
    root.mainloop()
