<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_oldjoin.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_rpc_oldjoin.sh

## Purpose
Blackbox/selftest shell script for Samba's net rpc oldjoin behavior. It drives the local test environment through `mkdir`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_rpc_oldjoin.sh SERVER PREFIX SMB_CONF_PATH`. Important routines are `test_smbpasswd (line 22)`. Key harness variables include `SERVER (line 10)`, `PREFIX (line 11)`, `SMB_CONF_PATH (line 12)`, `OPTIONS (line 20)`.

## Control Flow
The file is 49 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 40: testit "mkdir -p $privatedir" mkdir -p $privatedir || failed=$(expr $failed + 1)`, `line 41: testit "smbpasswd -a -m" \`, `line 44: testit "net_rpc_oldjoin" $VALGRIND $BINDIR/net rpc oldjoin -S $SERVER $OPTIONS || failed=$(expr $failed + 1)`, `line 45: testit "net_rpc_testjoin1" $VALGRIND $BINDIR/net rpc testjoin -S $SERVER $OPTIONS || failed=$(expr $failed + 1)`, `line 46: testit "net_rpc_changetrustpw" $VALGRIND $BINDIR/net rpc changetrustpw -S $SERVER $OPTIONS || failed=$(expr $failed + 1)`, `line 47: testit "net_rpc_testjoin2" $VALGRIND $BINDIR/net rpc testjoin -S $SERVER $OPTIONS || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `mkdir`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of mkdir, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_rpc_oldjoin.sh -->
