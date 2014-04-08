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

    def __init__(this, date, workperiods = []):
        this.date = date
        this.workperiods = workperiods
        this.activeperiod = None

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
                        datetime.strptime(string, "%H:%M"))

    def __str__(this):
        return "{}: {}-{}".format(this.timein.date(),
                                 this.timein.time(),
                                 this.timeout.time())

    def __init__(this, timein, timeout = None):
        this.timein = timein
        this.timeout = timeout

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
