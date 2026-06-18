<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb1_shadow_copy_torture.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smb1_shadow_copy_torture.sh

## Purpose
Blackbox/selftest shell script for Samba's smb1 shadow copy torture behavior. It drives the local test environment through `smbtorture`, `mkdir`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_shadow_copy SERVER SERVER_IP DOMAIN USERNAME PASSWORD WORKDIR SMBTORTURE`. Important routines are `build_files (line 32)`, `build_snapshots (line 41)`, `test_shadow_copy_openroot (line 53)`. Key harness variables include `SERVER (line 13)`, `SERVER_IP (line 14)`, `DOMAIN (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `WORKDIR (line 18)`, `SMBTORTURE (line 19)`, `SNAPSHOT (line 25)`.

## Control Flow
The file is 77 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 63: testit "opening shadow copy root of share over SMB1" \`.

## State and Persistence Behavior
State touched or modeled by this file includes snapshot directories. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbtorture`, `mkdir`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes snapshot directories, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbtorture, mkdir, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb1_shadow_copy_torture.sh -->
