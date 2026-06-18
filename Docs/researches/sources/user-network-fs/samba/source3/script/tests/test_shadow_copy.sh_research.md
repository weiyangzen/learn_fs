<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_shadow_copy.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_shadow_copy.sh

## Purpose
Blackbox/selftest shell script for Samba's shadow copy behavior. It drives the local test environment through `smbclient`, `ln`, `mkdir`, `rm`, `touch`, `grep`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_shadow_copy SERVER SERVER_IP DOMAIN USERNAME PASSWORD WORKDIR SMBCLIENT PARAMS`. Important routines are `build_files (line 49)`, `build_snapshots (line 97)`, `test_count_versions (line 137)`, `test_fetch_snap_file (line 211)`, `test_fetch_snap_dir (line 225)`, `test_shadow_copy_fixed (line 244)`, `test_shadow_copy_everywhere (line 299)`, `test_shadow_copy_format (line 373)`, `test_missing_basedir (line 397)`. Key harness variables include `SERVER (line 13)`, `SERVER_IP (line 14)`, `DOMAIN (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `WORKDIR (line 18)`, `SMBCLIENT (line 19)`, `ADDARGS (line 21)`, `SMBCLIENT (line 22)`.

## Control Flow
The file is 458 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 270: testit "$msg - regular file" \`, `line 274: testit "$msg - regular file in subdir" \`, `line 278: testit "$msg - regular file in case insensitive subdir" \`, `line 282: testit "$msg - local symlink" \`, `line 286: testit "$msg - abs symlink outside" \`, `line 290: testit "$msg - rel symlink outside" \`, `line 294: testit "$msg - list directory" \`, `line 312: testit "snapshots in each dir - regular file" \`, `line 316: testit "snapshots in each dir - regular file in subdir" \`, `line 320: testit "snapshots in each dir - local symlink (but outside snapshot)" \`; plus 13 more.

## State and Persistence Behavior
State touched or modeled by this file includes snapshot directories. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `ln`, `mkdir`, `rm`, `touch`, `grep`, `awk`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes snapshot directories, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, ln, mkdir, rm, touch, grep, awk paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_shadow_copy.sh -->
