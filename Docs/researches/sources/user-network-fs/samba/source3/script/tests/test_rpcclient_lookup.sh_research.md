<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_lookup.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_rpcclient_lookup.sh

## Purpose
Blackbox/selftest shell script for Samba's rpcclient lookup behavior. It drives the local test environment through `rpcclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_rpcclient_lookup.sh USERNAME PASSWORD SERVER RPCCLIENT`. Key harness variables include `USERNAME (line 14)`, `PASSWORD (line 15)`, `SERVER (line 16)`, `RPCCLIENT (line 17)`, `RPCCLIENTCMD (line 19)`, `RC (line 27)`, `RC (line 31)`, `RC (line 35)`, `RC (line 39)`.

## Control Flow
The file is 42 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 28: testit "lookupsids" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 32: testit "lookupsids_level" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 36: testit "lookupnames" test $RC -eq 0 || failed=$(expr $failed + 1)`, `line 40: testit "lookupnames_level" test $RC -eq 0 || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `rpcclient`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rpcclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_lookup.sh -->
