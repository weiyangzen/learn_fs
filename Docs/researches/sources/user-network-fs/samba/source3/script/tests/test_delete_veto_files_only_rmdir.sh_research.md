<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_delete_veto_files_only_rmdir.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_delete_veto_files_only_rmdir.sh

## Purpose
Blackbox/selftest shell script for Samba's delete veto files only rmdir behavior. It drives the local test environment through `smbclient`, `ln`, `mkdir`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER SERVER_IP USERNAME PASSWORD SHAREPATH SMBCLIENT`. Important routines are `test_dangle_symlink_delete_veto_rmdir (line 35)`, `test_dangle_symlink_veto_files_nodelete (line 106)`. Key harness variables include `SERVER (line 14)`, `SERVER_IP (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `SHAREPATH (line 18)`, `SMBCLIENT (line 19)`, `SMBCLIENT (line 21)`, `ADDARGS (line 22)`.

## Control Flow
The file is 182 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 173: testit "rmdir can delete directory containing dangling symlink" \`, `line 178: testit "rmdir cannot delete directory delete_veto_files_no containing dangling symlink" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `ln`, `mkdir`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, ln, mkdir, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_delete_veto_files_only_rmdir.sh -->
