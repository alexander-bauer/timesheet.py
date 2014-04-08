#!/usr/bin/python

import sys, argparse
from datetime import datetime, date, time
import os.path

FILEPATH = os.path.expanduser("~/.timesheets")
EPOCH = date(1970, 1, 1)        # UNIX EPOCH

class Timesheet:
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
        return datetime.combine(EPOCH, this.outtime) \
            - datetime.combine(EPOCH, this.intime)

    def __init__(this, timein, timeout = None):
        this.timein = timein
        this.timeout = timeout

@classmethod
def parseWorkperiod(cls, string):
    if "-" in string:
        splitstring = string.split("-")
        timein = datetime.strptime(splitstring[0], "%H:%M").time()
        timeout = datetime.strptime(splitstring[1], "%H:%M").time()
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
    parser.add_argument("check", action="store", choices=["in", "out"],
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
