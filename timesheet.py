#!/usr/bin/python

import sys, argparse, os.path, json
from datetime import datetime, date, time, timedelta


FILEPATH = os.path.expanduser("~/.timesheets")
EPOCH = date(1970, 1, 1)        # UNIX EPOCH
CURRENTDATE = datetime.now().date()


CHECK_IN = "in"
CHECK_OUT = "out"
CHECK_HIST = "hist"
SHOW_READABLE = "show"

class Timesheet:
    def completelatestwith(self, string):
        # Get the last workperiod and pass it the string to complete
        # it with.
        self.workperiods[-1].completewith(string)

    def newperiod(self, period):
        self.workperiods.append(period)
        if not period.iscomplete():
            self.activeperiod = None

    def save(self, filename):
        # Open the relevant file for writing.
        with open(filename, "w") as f:
            # Write the metadate as the header.
            f.write(self.date.strftime("%Y-%m-%d\n"))

            # Write all of the workperiods.
            for wp in self.workperiods:
                f.write(wp.timein.strftime(Workperiod.__timefmt__))
                if wp.timeout != None:
                    f.write(" " +
                            wp.timeout.strftime(Workperiod.__timefmt__))

                # Always append a trailing newline.
                f.write("\n")

    def complete_workperiods_on(self, date):
        # Ensure that the workperiod is both complete and for the
        # given date.
        return filter(lambda wp: wp.timeout and wp.timein.date() == date,
                      self.workperiods)

    def total_on_date(self, date):
        sumtime = timedelta()
        for wp in self.complete_workperiods_on(date):
            sumtime += wp.sumtime()
        return sumtime

    def __str__(self):
        as_str_list = []

        # Iterate over each day starting from the timesheet date.
        for offset in xrange(0, 14):
            # Adding a timedelta makes the date into a datetime, so we
            # need to strip it down again.
            curdate = (self.date + timedelta(days=offset)).date()

            workperiods = self.complete_workperiods_on(curdate)
            duration_formatted = ":".join(str(
                self.total_on_date(curdate)).split(":")[0:2])

            as_str_list.append("{0} {1} {2}".format(
                curdate, duration_formatted,
                " ".join([wp.short_str() for wp in workperiods])))

        return "\n".join(as_str_list)

    def __init__(self, date, workperiods = []):
        self.date = date
        self.workperiods = workperiods
        self.activeperiod = None


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
    def iscomplete(self):
        return (self.timein != None and self.timeout != None)

    def sumtime(self):
        # If the times are not both defined, return 0.
        if not self.iscomplete():
            return timedelta(seconds=0)

        # Return the difference of the times in and out. The times
        # should be pure datetime.time objects, so we convert them to
        # datetime objects starting from the UNIX Epoch.
        return self.timeout - self.timein

    def completewith(self, string):
        self.timeout = datetime.combine(CURRENTDATE,
            datetime.strptime(string, Workperiod.__shorttimefmt__))

    def short_str(self):
        if not self.iscomplete():
            return

        return "{}-{}".format(self.timein.strftime("%H:%M"),
                              self.timeout.strftime("%H:%M"))

    def __repr__(self):
        return "\"" + self.__str__() + "\""

    def __str__(self):
        return "{}: {}-{}".format(self.timein.date(),
                                 self.timein.strftime("%H:%M"),
                                  self.timeout.strftime("%H:%M"))

    def __init__(self, timein, timeout = None):
        self.timein = timein
        self.timeout = timeout

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
                        choices=[CHECK_IN, CHECK_OUT, CHECK_HIST,
                                 SHOW_READABLE],
                        help="check in or out")

    # Get the time at which to check in or out.
    parser.add_argument("time", action="store", nargs="?",
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
