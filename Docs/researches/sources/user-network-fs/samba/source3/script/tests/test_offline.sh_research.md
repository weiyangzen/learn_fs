<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_offline.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_offline.sh

## Purpose
Blackbox/selftest shell script for Samba's offline behavior. It drives the local test environment through `smbclient`, `touch`, `sed`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_offline SERVER SERVER_IP DOMAIN USERNAME PASSWORD WORKDIR SMBCLIENT`. Key harness variables include `SERVER (line 12)`, `SERVER_IP (line 13)`, `DOMAIN (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `WORKDIR (line 17)`, `SMBCLIENT (line 18)`, `SMBCLIENT (line 20)`, `ADDARGS (line 21)`.

## Control Flow
The file is 33 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 31: testit "file has offline attribute" test "x$attribs" = "x1000" || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `touch`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, touch, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_offline.sh -->
