<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_samlogon.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_rpcclient_samlogon.sh

## Purpose
Blackbox/selftest shell script for Samba's rpcclient samlogon behavior. It drives the local test environment through `rpcclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_rpcclient_samlogon.sh USERNAME PASSWORD binding <rpcclient commands>`. Important routines are `rpcclient_samlogon_schannel_seal (line 15)`, `rpcclient_samlogon_schannel_sign (line 20)`. Key harness variables include `USERNAME (line 10)`, `PASSWORD (line 11)`, `ADDARGS (line 13)`.

## Control Flow
The file is 32 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 27: testit "rpcclient dsenumdomtrusts" $VALGRIND $BINDIR/rpcclient $ADDARGS -U% -c "dsenumdomtrusts" || failed=$(expr $failed + 1)`, `line 28: testit "rpcclient getdcsitecoverage" $VALGRIND $BINDIR/rpcclient $ADDARGS -U% -c "getdcsitecoverage" || failed=$(expr $failed + 1)`, `line 29: testit "rpcclient samlogon schannel seal" rpcclient_samlogon_schannel_seal $ADDARGS || failed=$(expr $failed +1)`, `line 30: testit "rpcclient samlogon schannel sign" rpcclient_samlogon_schannel_sign $ADDARGS || failed=$(expr $failed +1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `rpcclient`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rpcclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient_samlogon.sh -->
