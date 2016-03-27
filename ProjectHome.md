# Overview #
**loghound** generates weekly operating and programming logs for [WMBR 88.1FM](http://wmbr.org)

Operating logs cover:
  * Hourly readings for room temperature and antenna forward and reflection power.
  * A tower light voltage check at sunset.
  * Random emergency alert system checks throughout the week.
  * Transmitter powerup and powerdown events.

Programming logs cover:
  * Which show is playing at a given time, including which DJ, engineer, and producer.
  * Which public service announcements and show promotions are played.
  * Sign-on and sign-off events.

WMBR has had computer-generated logs for quite some time. Loghound offers several improvements and fixes a few bugs.
# Improvements #

  * New look! The programming log has had the biggest makeover. We hope the new layout will be easier to check from a glance, easier for newcomers, and easier for weekly reviewers.

  * Code reduction. Starting with a 23-year-old codebase of over 12,000 lines that spanned 6 languages -- C, LaTeX, Perl, Applescript, Yacc, and [PL/I](http://en.wikipedia.org/wiki/PL/I#Sample_programs) -- we ended with under 1,000 lines of python plus pure python libraries. Less code means less bugs and easier maintenance.

  * Portability: loghound runs on any machine with python 2.5 or above (including all the WMBR station computers).

  * No installation. Just download and unzip -- required libraries and fonts are included.

  * Louder error messages. If loghound has trouble connecting to the internet to fetch the current show schedule, for example, it'll tell you about it.

  * Each page of logs now has its own signature page. No more flipping back and forth to fill in logs for your show.

  * Easier navigation: assuming duplex printing, dates and page numbers always appear on outside corners.

# Bug Fixes #
  * Layout issues. A long DJ list, for example, no longer pushes the right half of the programming logs off the page.
  * Formatting issues, including Unicode support.
  * Corrected daylight savings and sunset calculations.
  * Correct handling of alternating shows.
  * Reliable communication with WMBR's web server. (In the past it had been failing 80%+ of the time, requiring several attempts to create the logs.)