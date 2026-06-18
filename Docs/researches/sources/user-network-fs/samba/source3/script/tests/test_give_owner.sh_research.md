<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_give_owner.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_give_owner.sh

## Purpose
Blackbox/selftest shell script for Samba's give owner behavior. It drives the local test environment through `smbclient`, `net`, `smbcacls`, `rm`, `touch`, `grep`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 SERVER SERVER_IP USERNAME PASSWORD PREFIX SMBCLIENT SMBCACLS NET SHARE"`. Important routines are `setup_testfile (line 30)`, `remove_testfile (line 40)`, `set_win_owner (line 47)`, `win_owner_is (line 56)`, `add_ace (line 74)`, `chown_give_fails (line 114)`. Key harness variables include `SERVER (line 12)`, `SERVER_IP (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`, `PREFIX (line 16)`, `SMBCLIENT (line 17)`, `SMBCACLS (line 18)`, `NET (line 19)`, `SHARE (line 20)`, `SMBCLIENT (line 22)`; plus 2 more.

## Control Flow
The file is 147 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 128: testit "create testfile" setup_testfile $SHARE afile || failed=$(expr $failed + 1)`, `line 129: testit "verify owner" win_owner_is $SHARE afile "$SERVER/$USERNAME" || failed=$(expr $failed + 1)`, `line 132: testit "grant SeRestorePrivilege" $NET rpc rights grant $USERNAME SeRestorePrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || failed=$(expr $failed + 1)`, `line 133: testit "grant full rights" add_ace $SHARE afile "ACL:$SERVER\\$USERNAME:ALLOWED/0x0/FULL" || failed=$(expr $failed + 1)`, `line 136: testit "give owner with SeRestorePrivilege" set_win_owner $SHARE afile "$SERVER\user1" || failed=$(expr $failed + 1)`, `line 137: testit "verify owner" win_owner_is $SHARE afile "$SERVER/user1" || failed=$(expr $failed + 1)`, `line 138: testit "take owner" set_win_owner $SHARE afile "$SERVER\\$USERNAME" || failed=$(expr $failed + 1)`, `line 139: testit "verify owner" win_owner_is $SHARE afile "$SERVER/$USERNAME" || failed=$(expr $failed + 1)`, `line 142: testit "revoke SeRestorePrivilege" $NET rpc rights revoke $USERNAME SeRestorePrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || failed=$(expr $failed + 1)`, `line 143: testit "give owner without SeRestorePrivilege" chown_give_fails $SHARE afile "$SERVER\user1" NT_STATUS_INVALID_OWNER || failed=$(expr $failed + 1)`; plus 1 more.

## State and Persistence Behavior
State touched or modeled by this file includes temporary privilege grants. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `smbcacls`, `rm`, `touch`, `grep`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes temporary privilege grants, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, smbcacls, rm, touch, grep, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_give_owner.sh -->
