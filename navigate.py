#!/usr/bin/env python3.7
import sys
import os
import pickle
import pwd
import argparse

from prettytable import PrettyTable
from tracker import Tracker, Matcher, bcolors

# TODO: option to "redistribute" the score, e.g. if first entries are: 9,7,2,2:
#      update them to something like 7,6,4,4


def set_parser_args(parser: argparse.ArgumentParser):
    parser.add_argument("--input", type=str, default=""),
    parser.add_argument("--num", type=int, default="-1",),
    parser.add_argument("--change_from", default="-1"),
    parser.add_argument("--change_to", type=int, default="-1",),

    parser.add_argument("--init", action="store_true")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--path", action="store_true")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--open", action="store_true")


class Parser(argparse.ArgumentParser):
    def error(self, message):
        txt = {
            "--init": "Initialized/overwrites the dictionary for the given location.",
            "--fetch": "Updates the dictionary, untracked subdirs are added.",
            "--delete": "Removes the dictionary",
            "--show": "Same as -s, just the first n entries",
            "--path": "Returns the current path",
            "--update <num> <score>": "Alters the score of dictionary entry with number <num> ",
            "": "",
            "External commands:": "",
            "ut [<depth>]": "Shows the tree of the root directory. Optional: depth",
            "ul": "Lists the currently supported locations (by the script dic.py, ZSH)",
            "un <dir> [<dst>]": "Set new path (ZSH).",
        }

        t = PrettyTable(["Flags", "Description"])
        t.align["Flags"] = "l"
        t.align["Description"] = "l"
        t.padding_width = 0
        for key, val in txt.items():
            t.add_row([bcolors.OKGREEN + key + bcolors.ENDC, val])

        print(
            "\n" + bcolors.BOLD + bcolors.FAIL + "How to use Navigaterm?" + bcolors.ENDC
        )
        print(t)
        # print(
        #    "\nAll other inputs are treated as '"
        #    + bcolors.UNDERLINE
        #    + "search strings"
        #    + bcolors.ENDC
        #    + "':\nThe sorted dictionary is traversed top-bottom and checked whether input is part of the string.\n"
        #    + "If yes, cd to that dir, otherwise proceed.\n\nIf no dir was found, an error is thrown and directory rescanned."
        #    + bcolors.UNDERLINE
        # )
        sys.exit(2)


parser = Parser(description="Process some integers.")
set_parser_args(parser)
args = parser.parse_args()


# get the root-dir
user = pwd.getpwuid(os.getuid())[0]

wd = os.getenv("NAV")
try:
    with open(wd + "/.location") as s:
        loc = s.readline().strip()
except:
    loc = os.path.join("/Users", user)

loc_name = (
    loc.split("/")[-1] if loc[-1] != "/" else loc.split("/")[-2]
)  # name of the dictionary which is stored in navi_list

# print the current root folder
if args.path:
    print(bcolors.OKBLUE + "Current path: " + bcolors.ENDC + loc)
    exit()


if args.init:
    # initialize/overwrite the dictionary
    val = input(
        f"This will initialize/overwrite the history for this dir ({loc}). Continue? (y/n) "
    )
    if val.lower() == "y":
        tracker = Tracker(loc, loc_name, depth=3, init=True)
        tracker.save()
    exit()

tracker = Tracker(loc, loc_name, depth=3)

# print the first n sorted entries
if args.show:
    if args.num != -1:
        num = args.num
    else:
        num = 15

    print(bcolors.OKBLUE + "Top entries for " + loc_name + ":\n" + bcolors.ENDC)

    tracker.print(num)

# alters the dictionary: called by f.ex.: u -a 12 42
elif args.update:
    assert args.change_from != -1 and args.change_to != -1, (
        bcolors.FAIL
        + "Bad number of arguments."
        + bcolors.ENDC
        + "\nNeed two numbers: First one for the "
        + bcolors.OKBLUE
        + "entry number"
        + bcolors.ENDC
        + ", second one for the "
        + bcolors.OKBLUE
        + "new score."
        + bcolors.ENDC
    )

    tracker.set_dict_score(args.change_from, args.change_to)

elif args.delete:
    val = input(f"This will delete the history for this dir ({loc}). Continue? (y/n) ")
    if val == "y":
        tracker.remove_dict()
    else:
        print("Aborted.")


# update the dictionary
elif args.fetch:
    tracker.update()
    tracker.save()

# find a match, returns path for 'cd'
elif len(sys.argv) > 1:  # prefent from running if no args are given
    if not tracker.find_hit(
        args.input, match=Matcher.fuzzy, match_file=args.open, response=args.open
    ):  # find_hit called twice, if no match in first run, rescan dirs and try again
        if not args.open:
            tracker.update(True)  # silent
            tracker.save()

            tracker.find_hit(args.input, match=Matcher.fuzzy, response=False)

else:
    parser.error("no argument")
