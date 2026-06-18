<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_cred_change_at.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_cred_change_at.sh

## Purpose
Blackbox/selftest shell script for Samba's net cred change at behavior. It drives the local test environment through `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_cred_change_at.sh CONFIGURATION`. Important routines are `test_change_machine_secret_at (line 14)`.

## Control Flow
The file is 33 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 30: testit "change machine secret at" test_change_machine_secret_at || failed=$(("$failed" + 1))`, `line 31: testit "validate secret" $VALGRIND "$BINDIR/net rpc testjoin" "$@" || failed=$(("$failed" + 1))`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `grep`. Sourced/helper scripts include `. "$incdir/subunit.sh"`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_cred_change_at.sh -->
