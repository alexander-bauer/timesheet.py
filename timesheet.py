#!/usr/bin/python

import sys
from datetime import datetime

class Timesheet:
    def newweek(this, week):
        this.weeks.append(week)

    def __init__(this, weeks = []):
        this.weeks = weeks

class Week:
    def newday(this, workday):
        this.workdays.append(workday)

    def sumtime(this):
        # For each recorded weekday, sum the time and add it to the
        # total.
        total = 0
        for workday in this.workdays:
            total += workday.sumtime()
        
        return total

    def __init__(this, year = None, week = None, workdays = []):
        isocal = datetime.now().isocalendar() # (year, weeknum, weekday)
        if year == None: year = isocal[0]     # Set the current year
        if week == None: week = isocal[1]     # Set the current week day

        this.year = year
        this.week = week
        this.workdays = workdays

class Workday:
    def newperiod(this, workperiod):
        this.workperiods.append(workperiod)

    def sumtime(this):
        # For each set of times in and times out, sum their
        # difference.
        total = 0
        for workperiod in this.workperiods:
            total += workperiod.sumtime()

        return total

    def __init__(this, isoday = None, workperiods = []):
        if isoday == None: isoday = datetime.now().isocalendar()[2]

        this.isoday = isoday
        this.workperiods = workperiods

class Workperiod:
    def sumtime(this):
        # Return the difference of the times in and out.
        return this.outtime - this.intime

    def __init__(this, timein, timeout):
        this.timein = timein
        this.timeout = timeout

def main(argc, argv):
    pass

def promptdefault(prompt, default = None):
    # Attach some suffix to the end of the prompt. If the default is
    # given, include it.
    if default != None:
        prompt += " ({}): ".format(default)
    else:
        prompt += ": "

    # Print the prompt and take input as appropriate.
    userinput = raw_input(prompt)
    if len(userinput) > 0:
        return userinput
    else:
        return default

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
