<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_machine_account.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_machine_account.sh

## Purpose
Blackbox/selftest shell script for Samba's net machine account behavior. It drives the local test environment through `net`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 NET CONFFILE SERVER_IP"`. Important routines are `net_ads_user (line 21)`. Key harness variables include `NET (line 9)`, `CONFFILE (line 11)`, `SERVER_IP (line 13)`.

## Control Flow
The file is 34 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 32: testit "net_ads_user" net_ads_user || failed=$((failed + 1))`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `net`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_machine_account.sh -->
