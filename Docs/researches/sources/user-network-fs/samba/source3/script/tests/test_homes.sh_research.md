<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_homes.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_homes.sh

## Purpose
Blackbox/selftest shell script for Samba's homes behavior. It drives the local test environment through `smbclient`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: test_homes.sh SERVER USERNAME PASSWORD LOCAL_PATH PREFIX SMBCLIENT CONFIGURATION"`. Important routines are `test_gooduser_home (line 25)`, `test_eviluser_home (line 58)`, `test_slashuser_home (line 91)`. Key harness variables include `SERVER (line 11)`, `USERNAME (line 12)`, `PASSWORD (line 13)`, `LOCAL_PATH (line 14)`, `PREFIX (line 15)`, `SMBCLIENT (line 16)`, `CONFIGURATION (line 17)`, `USERNAME (line 33)`, `USERNAME (line 66)`, `USERNAME (line 99)`.

## Control Flow
The file is 136 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 124: testit "test gooduser home" \`, `line 128: testit "test eviluser home reject" \`, `line 132: testit "test slashuser home reject" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_homes.sh -->
