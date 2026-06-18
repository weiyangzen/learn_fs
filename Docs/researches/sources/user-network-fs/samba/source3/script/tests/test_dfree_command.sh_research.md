<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_dfree_command.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_dfree_command.sh

## Purpose
Blackbox/selftest shell script for Samba's dfree command behavior. It drives the local test environment through `smbclient`, `awk`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_dfree_command.sh SERVER DOMAIN USERNAME PASSWORD PREFIX SMBCLIENT`. Important routines are `test_smbclient_dfree (line 28)`. Key harness variables include `SERVER (line 14)`, `DOMAIN (line 15)`, `USERNAME (line 16)`, `PASSWORD (line 17)`, `PREFIX (line 18)`.

## Control Flow
The file is 69 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 28: test_smbclient_dfree()`, `line 37: subunit_start_test "$name"`, `line 43: subunit_pass_test "$name"`, `line 46: echo "$output" | subunit_fail_test "$name"`, `line 50: echo "$output" | subunit_fail_test "$name"`, `line 56: test_smbclient_dfree "Test dfree command share root SMB3" dfree "l" "2000 1024. 20" -U$USERNAME%$PASSWORD --option=clientmaxprotocol=SMB3 || failed=$(expr $failed + 1)`, `line 57: test_smbclient_dfree "Test dfree command subdir1 SMB3" dfree "cd subdir1; l" "8000 1024. 80" -U$USERNAME%$PASSWORD --option=clientmaxprotocol=SMB3 || failed=$(expr $faile`, `line 58: test_smbclient_dfree "Test dfree command subdir2 SMB3" dfree "cd subdir2; l" "32000 1024. 320" -U$USERNAME%$PASSWORD --option=clientmaxprotocol=SMB3 || failed=$(expr $fai`, `line 61: test_smbclient_dfree "Test dfree command share root NT1" dfree "l" "2000 1024. 20" -U$USERNAME%$PASSWORD --option=clientmaxprotocol=NT1 || failed=$(expr $failed + 1)`, `line 63: test_smbclient_dfree "Test dfree command subdir1 NT1" dfree "cd subdir1; l" "2000 1024. 20" -U$USERNAME%$PASSWORD --option=clientmaxprotocol=NT1 || failed=$(expr $failed `; plus 1 more.

## State and Persistence Behavior
State touched or modeled by this file includes fake disk-free configuration. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `awk`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes fake disk-free configuration, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, awk paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_dfree_command.sh -->
