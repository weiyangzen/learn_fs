<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_cred_change.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_cred_change.sh

## Purpose
Blackbox/selftest shell script for Samba's net cred change behavior. It drives the local test environment through shell builtins and harness helpers, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_cred_change.sh CONFIGURATION`.

## Control Flow
The file is 17 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 12: testit "1: change machine secret" $VALGRIND $BINDIR/wbinfo --change-secret || failed=$(expr $failed + 1)`, `line 13: testit "1: validate secret" $VALGRIND $BINDIR/net rpc testjoin "$@" || failed=$(expr $failed + 1)`, `line 14: testit "2: change machine secret" $VALGRIND $BINDIR/wbinfo --change-secret || failed=$(expr $failed + 1)`, `line 15: testit "2: validate secret" $VALGRIND $BINDIR/net rpc testjoin "$@" || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_cred_change.sh -->
