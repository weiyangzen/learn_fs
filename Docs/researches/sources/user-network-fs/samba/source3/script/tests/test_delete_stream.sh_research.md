<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_delete_stream.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_delete_stream.sh

## Purpose
Blackbox/selftest shell script for Samba's delete stream behavior. It drives the local test environment through `smbclient`, `net`, `smbcacls`, `mkdir`, `rm`, `touch`; plus 2 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 SERVER SERVER_IP USERNAME PASSWORD PREFIX SMBCLIENT SMBCACLS NET SHARE"`. Important routines are `setup_testfile (line 30)`, `remove_testfile (line 51)`, `set_win_owner (line 59)`, `delete_stream (line 66)`, `win_owner_is (line 89)`. Key harness variables include `SERVER (line 12)`, `SERVER_IP (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`, `PREFIX (line 16)`, `SMBCLIENT (line 17)`, `SMBCACLS (line 18)`, `NET (line 19)`, `SHARE (line 20)`, `SMBCLIENT (line 22)`; plus 2 more.

## Control Flow
The file is 123 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 105: testit "create testfile" setup_testfile $SHARE || exit 1`, `line 108: testit "grant SeRestorePrivilege" $NET rpc rights grant $USERNAME SeRestorePrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || exit 1`, `line 111: testit "give owner with SeRestorePrivilege" set_win_owner "$SERVER\user1" || exit 1`, `line 112: testit "verify owner" win_owner_is "$SERVER/user1" || exit 1`, `line 115: testit "delete stream" delete_stream $SHARE afile || exit 1`, `line 118: testit "remove testfile" remove_testfile $SHARE || exit 1`, `line 121: testit "revoke SeRestorePrivilege" $NET rpc rights revoke $USERNAME SeRestorePrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || exit 1`.

## State and Persistence Behavior
State touched or modeled by this file includes temporary privilege grants. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `smbcacls`, `mkdir`, `rm`, `touch`, `grep`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes temporary privilege grants, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, smbcacls, mkdir, rm, touch, grep, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_delete_stream.sh -->
