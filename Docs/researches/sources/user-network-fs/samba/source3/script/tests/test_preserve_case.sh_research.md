<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_preserve_case.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_preserve_case.sh

## Purpose
Blackbox/selftest shell script for Samba's preserve case behavior. It drives the local test environment through `smbclient`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_preserve_case.sh SERVER DOMAIN USERNAME PASSWORD PREFIX SMBCLIENT`. Important routines are `test_smbclient (line 34)`. Key harness variables include `SERVER (line 14)`, `DOMAIN (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `PREFIX (line 18)`, `PROTOCOL_LIST (line 21)`, `PROTOCOL_LIST (line 24)`, `SHARE (line 52)`, `SHARE (line 68)`.

## Control Flow
The file is 86 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 34: test_smbclient()`, `line 41: subunit_start_test "$name"`, `line 45: subunit_pass_test "$name"`, `line 47: echo "$output" | subunit_fail_test "$name"`, `line 55: test_smbclient "Test lowercase ls 1 ($PROTOCOL)" $SHARE "ls 1" -U$USERNAME%$PASSWORD -m$PROTOCOL || failed=$(expr $failed + 1)`, `line 56: test_smbclient "Test lowercase get 1 ($PROTOCOL)" $SHARE "get 1 LOCAL_1" -U$USERNAME%$PASSWORD -m$PROTOCOL || failed=$(expr $failed + 1)`, `line 59: test_smbclient "Test lowercase ls A ($PROTOCOL)" $SHARE "ls A" -U$USERNAME%$PASSWORD -m$PROTOCOL || failed=$(expr $failed + 1)`, `line 60: test_smbclient "Test lowercase get A ($PROTOCOL)" $SHARE "get A LOCAL_A" -U$USERNAME%$PASSWORD -m$PROTOCOL || failed=$(expr $failed + 1)`, `line 63: test_smbclient "Test lowercase ls z ($PROTOCOL)" $SHARE "ls z" -U$USERNAME%$PASSWORD -m$PROTOCOL || failed=$(expr $failed + 1)`, `line 64: test_smbclient "Test lowercase get z ($PROTOCOL)" $SHARE "get z LOCAL_Z" -U$USERNAME%$PASSWORD -m$PROTOCOL || failed=$(expr $failed + 1)`; plus 7 more.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_preserve_case.sh -->
