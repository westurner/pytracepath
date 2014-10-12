#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
"""
pytracepath
"""

import subprocess
import collections

TraceHop = collections.namedtuple(
    'TraceHop',
    ('hopn', 'host', 'time', 'otherstr', 'n')
)


def pytracepath(host=None, resolvedns=False):
    """
    wrap tracepath
    """
    if host is None:
        raise Exception()

    args = ['tracepath']
    if resolvedns is False:
        args.append('-n')
    args.append(host)

    p = subprocess.Popen(
        args=args,
        stdout=subprocess.PIPE)

    output = p.stdout  # list(p.stdout)
    for line in output:
        _line = line.strip()
        fields = _line.split()
        try:
            hopn = int(fields[0].rstrip(':'))  # try/except ValueError
        except ValueError:
            yield _line
            continue

        _host = fields[1]
        host = _host

        _time = fields[2]
        try:
            if _time.endswith('ms'):
                time = _time.rstrip('ms')
                time = float(time)
            else:
                time = _time
        except ValueError:
            time = _time

        # these are conditional on response type

        _otherstr = fields[3]
        # in ['pmtu','asymm','reached']
        otherstr = _otherstr

        n = None
        if len(fields) > 4:
            _n = fields[4]
            try:
                n = int(_n)
            except ValueError:
                n = _n
        yield TraceHop(hopn, host, time, otherstr, n)


def print_pytracepath(host):
    for line in pytracepath(host):
        print(line)


def build_graph(host):
    prev = None
    for line in pytracepath(host):
        if isinstance(line, TraceHop):
            if prev is None:
                continue
            yield (prev.host, line.host)


def print_graph(host):
    for l in build_graph(host):
        print(l)


import unittest


class Test_pytracepath(unittest.TestCase):
    def test_pytracepath(self):
        output = pytracepath('127.0.0.1')
        output = list(output)
        self.assertEqual(output, 0)


def main():
    import optparse
    import logging

    prs = optparse.OptionParser(usage="./%prog : args")

    # PEP8: ignore E127
    prs.add_option('-v', '--verbose',
                    dest='verbose',
                    action='store_true',)
    prs.add_option('-q', '--quiet',
                    dest='quiet',
                    action='store_true',)
    prs.add_option('-t', '--test',
                    dest='run_tests',
                    action='store_true',)

    (opts, args) = prs.parse_args()

    if not opts.quiet:
        logging.basicConfig()

        if opts.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    if opts.run_tests:
        import sys
        sys.argv = [sys.argv[0]] + args
        import unittest
        exit(unittest.main())

    host = args[0]
    print_pytracepath(host)

if __name__ == "__main__":
    main()
