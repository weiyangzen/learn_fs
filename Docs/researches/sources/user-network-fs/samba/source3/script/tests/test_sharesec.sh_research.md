<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_sharesec.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_sharesec.sh

## Purpose
Blackbox/selftest shell script for Samba's sharesec behavior. It drives the local test environment through `net`, `sharesec`, `grep`, `sed`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_sharesec.sh SERVERCONFFILE SHARESEC NET SHARE`. Key harness variables include `CONF (line 17)`, `SHARESEC (line 18)`, `NET (line 19)`, `SHARE (line 20)`, `CMD (line 22)`, `NET_CMD (line 23)`, `COUNT (line 33)`, `ACL (line 35)`, `OWNER (line 38)`, `GROUP (line 41)`; plus 17 more.

## Control Flow
The file is 148 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 30: testit "Set new ACL" $CMD --replace S-1-1-0:ALLOWED/0x0/READ ||`, `line 32: testit "Query new ACL" $CMD --view || failed=$(expr $failed + 1)`, `line 34: testit "Verify new ACL count" test $COUNT -eq 1 || failed=$(expr $failed + 1)`, `line 36: testit "Verify new ACL" test $ACL = S-1-1-0:ALLOWED/0x0/READ`, `line 39: testit "Verify empty OWNER" test "$OWNER" = "OWNER:" ||`, `line 42: testit "Verify empty GROUP" test "$GROUP" = "GROUP:" ||`, `line 45: testit "Verify control flags" test "$CONTROL" = "SR|DP" ||`, `line 48: testit "Add second ACL entry" $CMD --add S-1-5-32-544:ALLOWED/0x0/FULL ||`, `line 50: testit "Query ACL with two entries" $CMD --view ||`, `line 53: testit "Verify ACL count with two entries" test $COUNT -eq 2 ||`; plus 33 more.

## State and Persistence Behavior
State touched or modeled by this file includes share security descriptors.

## Dependencies and Integration Points
External command integrations: `net`, `sharesec`, `grep`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes share security descriptors, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, sharesec, grep, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_sharesec.sh -->
