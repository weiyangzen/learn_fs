<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_shadow_copy_torture.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_shadow_copy_torture.sh

## Purpose
Blackbox/selftest shell script for Samba's shadow copy torture behavior. It drives the local test environment through `smbclient`, `smbtorture`, `ln`, `mkdir`, `rm`, `touch`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_shadow_copy SERVER SERVER_IP DOMAIN USERNAME PASSWORD WORKDIR SMBTORTURE SMBCLIENT`. Important routines are `build_files (line 33)`, `build_snapshots (line 45)`, `build_stream_on_snapshot (line 59)`, `test_shadow_copy_write (line 66)`, `test_shadow_copy_stream (line 86)`, `test_shadow_copy_openroot (line 115)`, `test_shadow_copy_fix_inodes (line 134)`, `build_hiddenfile (line 152)`, `test_hiddenfile (line 172)`, `test_shadow_copy_listdir_fix_inodes (line 193)`. Key harness variables include `SERVER (line 13)`, `SERVER_IP (line 14)`, `DOMAIN (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `WORKDIR (line 18)`, `SMBTORTURE (line 19)`, `SMBCLIENT (line 20)`, `SNAPSHOT (line 26)`.

## Control Flow
The file is 227 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 76: testit "writing to shadow copy of a file" \`, `line 96: subunit_start_test msg`, `line 97: subunit_skip_test msg <<EOF`, `line 103: testit "reading stream of a shadow copy of a file" \`, `line 125: testit "opening shadow copy root of share" \`, `line 203: testit "$msg" \`, `line 221: testit "fix inodes with hardlink" test_shadow_copy_fix_inodes || failed=$(expr $failed + 1)`, `line 223: testit "Test reading DOS attribute" test_hiddenfile || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
State touched or modeled by this file includes snapshot directories. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbtorture`, `ln`, `mkdir`, `rm`, `touch`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes snapshot directories, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbtorture, ln, mkdir, rm, touch, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_shadow_copy_torture.sh -->
