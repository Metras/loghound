#!/usr/bin/python

# Modified 1/10/89 MAM - attempted fix of float/int problem
#                        and day calculation
#          3/27/92 MAM - leap year calculation now in load_dates()
#                        (where it should have been all along...)
#         10/26/09 AHM - translated this to python
#                        trimming out obsolete date calculation code

import datetime, calendar, math

day_of_year = lambda d: int(d.strftime("%j"))

TOWER_LATITUDE      = 42.361667
TOWER_LONGITUDE     = 71.084167
CIVIL_TWILIGHT_SINE = -0.10453

# to keep things as portable as possible, we will do the
# timezone calculations right here
# TODO CONSIDER HOW BAD THIS MIGHT BE!
#  If timezone law ever changes, we have to change this file
NORMAL_ZONE         = 5
DST_ZONE            = 4
# return the offset for a particular date
def offset(date):
  # daylight saving time begins on the second sunday of march
  # daylight saving time ends   on the first  sunday of november
  a = day_of_year([datetime.date(date.year,03,i) for i in xrange(1,32) if
        datetime.date(date.year,03,i).weekday() == calendar.SUNDAY][1])
  b = day_of_year([datetime.date(date.year,11,i) for i in xrange(1,31) if
        datetime.date(date.year,11,i).weekday() == calendar.SUNDAY][0])
  if day_of_year(date) >= a and day_of_year(date) < b:
    return DST_ZONE
  return NORMAL_ZONE

sind = lambda x: math.sin(math.pi*x/180.)
cosd = lambda x: math.cos(math.pi*x/180.)

# twilight will accept a date/datetime object from the datetime module
# as an argument and returns a datetime object
def twilight(date):
  tau = 0.985647 * (day_of_year(date) - 1)
  sintau  = sind(  tau)
  sintau2 = sind(2*tau)
  costau  = cosd(  tau)
  costau2 = cosd(2*tau)
  solar_longitude = 279.93418 + tau       \
                    + 1.914827 * sintau   \
                    - 0.079525 * costau   \
                    + 0.019938 * sintau2  \
                    - 0.00162  * costau2

  declination = 57.29578 * math.asin(0.39781 * sind(solar_longitude))

  meridian_transit = 12.0                  \
                     + 0.12357  * sintau   \
                     - 0.04289  * costau   \
                     + 0.153809 * sintau2  \
                     + 0.060783 * costau2
  
  hour_angle = CIVIL_TWILIGHT_SINE         \
                  - sind(TOWER_LATITUDE) * sind(declination)
  hour_angle = hour_angle / (cosd(TOWER_LATITUDE) * cosd(declination))
  hour_angle = 57.29578 * math.acos(hour_angle) / 15.0

  evening = meridian_transit + hour_angle + (TOWER_LONGITUDE / 15.0)
  twilight = int(3600.0 * evening - 3600.0 * offset(date))
  return datetime.datetime(date.year, date.month, date.day,\
                           twilight / 3600,
                           (twilight % 3600)/60,
                           twilight % 60)
