<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_fruit_resource_stream.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_fruit_resource_stream.sh

## Purpose
Blackbox/selftest shell script for Samba's fruit resource stream behavior. It drives the local test environment through `smbclient`, `rm`, `touch`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER SHARE USERNAME PASSWORD LOCAL_PATH SMBCLIENT`. Important routines are `put_then_delete_file (line 27)`. Key harness variables include `SERVER (line 14)`, `SHARE (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `LOCAL_PATH (line 18)`, `SMBCLIENT (line 19)`, `SMBCLIENT (line 20)`.

## Control Flow
The file is 41 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 36: testit "resource_stream" put_then_delete_file || failed=$((failed + 1))`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rm`, `touch`. Sourced/helper scripts include `. "$incdir/subunit.sh"`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rm, touch paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_fruit_resource_stream.sh -->
