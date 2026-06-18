<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_large_acl.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_large_acl.sh

## Purpose
Blackbox/selftest shell script for Samba's large acl behavior. It drives the local test environment through `smbclient`, `smbcacls`, `rm`, `touch`, `sed`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER USERNAME PASSWORD SMBCLIENT SMBCACLS PARAMS`. Important routines are `build_files (line 29)`, `cleanup (line 36)`, `test_large_acl (line 43)`. Key harness variables include `SERVER (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`, `SMBCLIENT (line 16)`, `SMBCACLS (line 17)`, `ADDARGS (line 19)`, `SMBCLIENT (line 20)`, `SMBCACLS (line 21)`.

## Control Flow
The file is 61 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 57: testit "able to retrieve a large ACL if VFS supports it" test_large_acl || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcacls`, `rm`, `touch`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcacls, rm, touch, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_large_acl.sh -->
