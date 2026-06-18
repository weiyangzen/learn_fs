<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_join_creds.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_rpc_join_creds.sh

## Purpose
Blackbox/selftest shell script for Samba's net rpc join creds behavior. It drives the local test environment through `mkdir`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_rpc_join_creds.sh  DOMAIN USERNAME PASSWORD SERVER PREFIX`. Key harness variables include `DOMAIN (line 10)`, `USERNAME (line 11)`, `PASSWORD (line 12)`, `SERVER (line 13)`, `PREFIX (line 14)`, `ADDARGS (line 16)`.

## Control Flow
The file is 30 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 24: testit "net_rpc_join_creds" $VALGRIND $BINDIR/net rpc join -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFIX/private -A`, `line 25: testit "net_rpc_testjoin_creds" $VALGRIND $BINDIR/net rpc testjoin -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFIX/pr`, `line 26: testit "net_rpc_changetrustpw_creds" $VALGRIND $BINDIR/net rpc changetrustpw -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=`, `line 27: testit "net_rpc_testjoin2_creds" $VALGRIND $BINDIR/net rpc testjoin -S $SERVER --option=netbiosname=netrpcjointest --option=domainlogons=yes --option=privatedir=$PREFIX/p`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `mkdir`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of mkdir, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_join_creds.sh -->
