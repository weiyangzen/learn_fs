<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclientsrvsvc.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_rpcclientsrvsvc.sh

## Purpose
Blackbox/selftest shell script for Samba's rpcclientsrvsvc behavior. It drives the local test environment through `rpcclient`, `grep`, `sed`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_rpcclientsrvsvc.sh USERNAME PASSWORD SERVER RPCCLIENT SHARE1`. Key harness variables include `USERNAME (line 14)`, `PASSWORD (line 15)`, `SERVER (line 16)`, `RPCCLIENT (line 17)`, `SHARE1 (line 18)`, `RPCCLIENTCMD (line 20)`, `SHARENAME (line 22)`, `MAX_USERS (line 23)`, `COMMENT (line 24)`, `RC (line 34)`; plus 10 more.

## Control Flow
The file is 90 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 35: testit "getinfo on S$SHARE1" test $RC = 0 || failed=$(expr $failed + 1)`, `line 39: testit "verifying $SHARE1 path" test -n "$SHAREPATH" ||`, `line 46: testit "netshareadd" test $RC = 0 || failed=$(expr $failed + 1)`, `line 55: testit "verifying comment" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 63: testit "verifying share path" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 69: testit "set csc policy" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 75: testit "verifying csc policy" test $CSC_CACHING_RET -eq 3 ||`, `line 82: testit "deleting share" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 88: testit "querying deleted share" test $RC -eq 1 || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `rpcclient`, `grep`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rpcclient, grep, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclientsrvsvc.sh -->
