<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_share_allowedusers.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_rpc_share_allowedusers.sh

## Purpose
Blackbox/selftest shell script for Samba's net rpc share allowedusers behavior. It drives the local test environment through `net`, `mkdir`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_rpc_share_allowedusers.sh  SERVER USERNAME PASSWORD PREFIX`. Key harness variables include `SERVER (line 10)`, `USERNAME (line 11)`, `PASSWORD (line 12)`, `PREFIX (line 13)`, `ADDARGS (line 15)`.

## Control Flow
The file is 49 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 22: testit_grep "net_usersidlist" '^ S-1-1-0$' $VALGRIND $net usersidlist $ADDARGS || failed=$(expr $failed + 1)`, `line 24: testit_grep "net_rpc_share_allowedusers" '^print\$$' $net usersidlist | $VALGRIND $net rpc share allowedusers -S$SERVER -U$USERNAME%$PASSWORD $ADDARGS || failed=$(expr $f`, `line 26: testit_grep "net_rpc_share_allowedusers" '^print\$$' $net usersidlist | $VALGRIND $net rpc share allowedusers -S$SERVER -U$USERNAME%$PASSWORD $ADDARGS - 'print$' || faile`, `line 28: testit_grep "net_rpc_share_allowedusers" '^ user1$' $net usersidlist | $VALGRIND $net rpc share allowedusers -S$SERVER -U$USERNAME%$PASSWORD $ADDARGS || failed=$(expr $fa`, `line 38: subunit_start_test "net_rpc_share_allowedusers"`, `line 42: subunit_pass_test "net_rpc_share_allowedusers"`, `line 46: echo "$multi_userout" | subunit_fail_test "net_rpc_share_allowedusers"`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `net`, `mkdir`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, mkdir, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_share_allowedusers.sh -->
