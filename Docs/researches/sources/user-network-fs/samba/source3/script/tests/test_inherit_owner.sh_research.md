<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_inherit_owner.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_inherit_owner.sh

## Purpose
Blackbox/selftest shell script for Samba's inherit owner behavior. It drives the local test environment through `smbclient`, `net`, `smbcacls`, `chown`, `mkdir`, `rm`; plus 4 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER USERNAME PASSWORD PREFIX SMBCLIENT SMBCACLS NET SHARE INH_WIN INH_UNIX <additional args>`. Important routines are `create_file (line 33)`, `create_dir (line 45)`, `cleanup_file (line 56)`, `cleanup_dir (line 65)`, `set_win_owner (line 74)`, `unix_owner_id_is (line 82)`, `get_unix_id (line 95)`, `win_owner_is (line 103)`. Key harness variables include `SERVER (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `PREFIX (line 17)`, `SMBCLIENT (line 18)`, `SMBCACLS (line 19)`, `NET (line 20)`, `SHARE (line 21)`, `INH_WIN (line 22)`, `INH_UNIX (line 23)`; plus 19 more.

## Control Flow
The file is 170 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 149: testit "$TEST_LABEL - setup root dir" create_dir tmp tmp.$$`, `line 150: testit "grant SeRestorePrivilege" $NET rpc rights grant $USERNAME SeRestorePrivilege -U $USERNAME%$PASSWORD -I $SERVER || exit 1`, `line 151: testit "$TEST_LABEL - assign default ACL" $SMBCACLS //$SERVER/tmp tmp.$$ -U $USERNAME%$PASSWORD -S "REVISION:1,OWNER:$SERVER\force_user,GROUP:$SERVER\domusers,ACL:Everyon`, `line 154: testit "$TEST_LABEL - create subdir under root" create_dir $SHARE tmp.$$/subdir`, `line 155: testit "$TEST_LABEL - verify subdir win owner" win_owner_is $SHARE tmp.$$/subdir "$WIN_OWNER_AFTER_CREATE"`, `line 156: testit "$TEST_LABEL - verify subdir unix owner" unix_owner_id_is $SHARE tmp.$$/subdir $UNIX_OWNER_AFTER_CREATE`, `line 157: testit "$TEST_LABEL - create file under root" create_file $SHARE tmp.$$/afile`, `line 158: testit "$TEST_LABEL - verify file win owner" win_owner_is $SHARE tmp.$$/afile "$WIN_OWNER_AFTER_CREATE"`, `line 159: testit "$TEST_LABEL - verify file unix owner" unix_owner_id_is $SHARE tmp.$$/afile $UNIX_OWNER_AFTER_CREATE`, `line 160: testit "$TEST_LABEL - change dir owner" set_win_owner $SHARE tmp.$$/subdir "$SERVER\smbget_user"`; plus 9 more.

## State and Persistence Behavior
State touched or modeled by this file includes temporary privilege grants. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `smbcacls`, `chown`, `mkdir`, `rm`, `touch`, `grep`, `awk`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes temporary privilege grants, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, smbcacls, chown, mkdir, rm, touch, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_inherit_owner.sh -->
