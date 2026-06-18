<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb2_not_casesensitive.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smb2_not_casesensitive.sh

## Purpose
Blackbox/selftest shell script for Samba's smb2 not casesensitive behavior. It drives the local test environment through `smbclient`, `rm`, `touch`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_smb2_not_casesensitive SERVER SERVER_IP USERNAME PASSWORD LOCAL_PATH SMBCLIENT`. Important routines are `test_access_with_different_case (line 26)`, `test_rename (line 48)`. Key harness variables include `SERVER (line 13)`, `SERVER_IP (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `LOCAL_PATH (line 17)`, `SMBCLIENT (line 18)`.

## Control Flow
The file is 81 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 73: testit "accessing a file with different case succeeds" \`, `line 77: testit "renaming a file with different case succeeds" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rm`, `touch`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rm, touch paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb2_not_casesensitive.sh -->
