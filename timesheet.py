#!/usr/bin/python

import sys, argparse
from datetime import datetime, date, time
import os.path

FILEPATH = os.path.expanduser("~/.timesheets")
EPOCH = date(1970, 1, 1)        # UNIX EPOCH
CURRENTDATE = datetime.now().date()


CHECK_IN = "in"
CHECK_OUT = "out"
CHECK_HIST = "hist"

class Timesheet:
    def completelatestwith(this, string):
        # Get the last workperiod and pass it the string to complete
        # it with.
        this.workperiods[-1].completewith(string)

    def newperiod(this, period):
        this.workperiods.append(period)
        if not period.iscomplete():
            this.activeperiod = None

    def save(this, filename):
        # Open the relevant file for writing.
        with open(filename, "w") as f:
            # Write the metadate as the header.
            f.write(this.date.strftime("%Y-%m-%d\n"))

            # Write all of the workperiods.
            for wp in this.workperiods:
                f.write(wp.timein.strftime(Workperiod.__timefmt__))
                if wp.timeout != None:
                    f.write(" " +
                            wp.timeout.strftime(Workperiod.__timefmt__)
                            + "\n")

    def __init__(this, date, workperiods = []):
        this.date = date
        this.workperiods = workperiods
        this.activeperiod = None


@classmethod
def latestTimesheet(cls, date=CURRENTDATE):
    return datetime(year=2014, month=4, day=6)

Timesheet.latest = latestTimesheet

@classmethod
def loadTimesheet(cls, filename):
    # Open the file.
    with open(filename, "r") as f:
        # Begin setting up the timesheet by reading the first line.
        metadate = datetime.strptime(f.readline().strip(), "%Y-%m-%d")
        newts = Timesheet(metadate)

        # Now that the timesheet is set up, we can fill out the rest
        # of the Workperiod items.
        for line in f:
            print line
            # Declare an empty workperiod to begin filling out.
            lineparts = line.split()

            if len(lineparts) >= 2:
                timein = datetime.strptime(" ".join(lineparts[0:2]),
                                           Workperiod.__timefmt__)

            if len(lineparts) >= 4:
                timeout = datetime.strptime(" ".join(lineparts[2:4]),
                                            Workperiod.__timefmt__)
            else:
                timeout = None

            if len(lineparts) >= 5:
                descriptor = lineparts[4]

            newts.workperiods.append(Workperiod(timein, timeout))

        return newts

Timesheet.load = loadTimesheet

class Workperiod:
    def iscomplete(this):
        return (this.timein != None and this.timeout != None)

    def sumtime(this):
        # Return the difference of the times in and out. The times
        # should be pure datetime.time objects, so we convert them to
        # datetime objects starting from the UNIX Epoch.
        return this.timeout - this.timein

    def completewith(this, string):
        this.timeout = datetime.combine(CURRENTDATE,
            datetime.strptime(string, Workperiod.__shorttimefmt__))

    def __repr__(this):
        return "\"" + this.__str__() + "\""

    def __str__(this):
        return "{}: {}-{}".format(this.timein.date(),
                                 this.timein.time(),
                                 this.timeout.time())

    def __init__(this, timein, timeout = None):
        this.timein = timein
        this.timeout = timeout

Workperiod.__timefmt__ = "%Y-%m-%d %H:%M"
Workperiod.__shorttimeft__ = "%H:%M"

@classmethod
def parseWorkperiod(cls, string):
    # Split the string into a timein and timeout, if applicable,
    # and parse them. Timeout can be omitted.
    splitstring = string.split("-")
    timein = datetime.combine(CURRENTDATE,
                    datetime.strptime(splitstring[0], "%H:%M").time())
    if len(splitstring) > 1:
        timeout = datetime.combine(CURRENTDATE,
                    datetime.strptime(splitstring[1], "%H:%M").time())
    else:
        timeout = None

    return cls(timein, timeout)

Workperiod.parse = parseWorkperiod

def main(argc, argv):
    flags = parseflags(argv[1:])
    


def parseflags(args):
    parser = argparse.ArgumentParser(description=
                                     "Manage timesheets.")
    # Get the file path if given.
    parser.add_argument("--file", "-f", action="store",
                        default=FILEPATH,
                        help="path to timesheet directory")

    # Get the department of work to be done.
    parser.add_argument("--department", "-d", action="store",
                        required=False, help="department or descriptor \
                        to record time for")

    # Determine whether the type is in or out.
    parser.add_argument("check", action="store",
                        choices=[CHECK_IN, CHECK_OUT, CHECK_HIST],
                        help="check in or out")

    # Get the time at which to check in or out.
    parser.add_argument("time", action="store",
                        default=datetime.now().strftime("%H:%M"),
                        help="time to check in or out at")

    return parser.parse_args(args)

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
