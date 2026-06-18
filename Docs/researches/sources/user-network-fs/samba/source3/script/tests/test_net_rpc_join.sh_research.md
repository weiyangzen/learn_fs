<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_join.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_rpc_join.sh

## Purpose
Blackbox/selftest shell script for Samba's net rpc join behavior. It drives the local test environment through `mkdir`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_rpc_join.sh  USERNAME PASSWORD SERVER PREFIX`. Key harness variables include `USERNAME (line 10)`, `PASSWORD (line 11)`, `SERVER (line 12)`, `PREFIX (line 13)`, `ADDARGS (line 15)`.

## Control Flow
The file is 25 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 20: testit "net_rpc_join" $VALGRIND $BINDIR/net rpc join -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFIX/private -U$USERN`, `line 21: testit "net_rpc_testjoin" $VALGRIND $BINDIR/net rpc testjoin -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFIX/private `, `line 22: testit "net_rpc_changetrustpw" $VALGRIND $BINDIR/net rpc changetrustpw -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFI`, `line 23: testit "net_rpc_testjoin2" $VALGRIND $BINDIR/net rpc testjoin -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFIX/private`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `mkdir`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of mkdir paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_join.sh -->
