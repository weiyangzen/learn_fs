<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_bad_auditnames.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_bad_auditnames.sh

## Purpose
Blackbox/selftest shell script for Samba's bad auditnames behavior. It drives the local test environment through `smbclient`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER SHARE USERNAME PASSWORD SMBCLIENT`. Important routines are `can_connect (line 24)`. Key harness variables include `SERVER (line 14)`, `SHARE (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `SMBCLIENT (line 18)`, `SMBCLIENT (line 19)`.

## Control Flow
The file is 29 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 29: testit "Cannot connect to share $SHARE" can_connect || failed=$((failed + 1))`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`, `grep`. Sourced/helper scripts include `. "$incdir/subunit.sh"`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_bad_auditnames.sh -->
