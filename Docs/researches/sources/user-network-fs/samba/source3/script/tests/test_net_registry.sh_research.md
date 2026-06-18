<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_registry.sh

## Purpose
Blackbox/selftest shell script for Samba's net registry behavior. It drives the local test environment through `net`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_registry.sh SCRIPTDIR SERVERCONFFILE NET CONFIGURATION RPC`. Important routines are `test_enumerate (line 36)`, `test_getsd (line 43)`, `test_enumerate_nonexisting (line 50)`, `test_enumerate_no_key (line 63)`, `test_create_existing (line 74)`, `test_createkey (line 93)`, `test_deletekey (line 131)`, `test_deletekey_nonexisting (line 178)`, `test_createkey_with_subkey (line 196)`, `test_deletekey_with_subkey (line 225)`, `test_setvalue (line 250)`, `test_deletevalue (line 290)`; plus 2 more. Key harness variables include `SCRIPTDIR (line 17)`, `SERVERCONFFILE (line 18)`, `NET (line 19)`, `CONFIGURATION (line 20)`, `RPC (line 21)`, `NET (line 23)`, `NETREG (line 26)`, `NETREG (line 28)`, `KEY (line 38)`, `KEY (line 45)`; plus 48 more.

## Control Flow
The file is 411 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 332: testit "enumerate HKLM" \`, `line 336: testit "enumerate nonexisting hive" \`, `line 340: testit "enumerate without key" \`, `line 346: testit "getsd HKLM" \`, `line 351: testit "create existing HKLM" \`, `line 355: testit "create key" \`, `line 359: testit "delete key" \`, `line 363: testit "delete^2 key" \`, `line 367: testit "enumerate nonexisting key" \`, `line 371: testit "create key with subkey" \`; plus 9 more.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values.

## Dependencies and Integration Points
External command integrations: `net`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry.sh -->
