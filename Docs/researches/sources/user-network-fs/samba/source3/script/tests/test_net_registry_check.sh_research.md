<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry_check.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_registry_check.sh

## Purpose
Blackbox/selftest shell script for Samba's net registry check behavior. It drives the local test environment through `net`, `grep`, `sed`, `cp`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: test_net_registry_check.sh SCRIPTDIR SERVERCONFFILE NET CONFIGURATION DBWRAP_TOOL"`. Important routines are `regcheck (line 30)`, `regrepair (line 37)`, `checkerr (line 43)`, `regchecknrepair (line 51)`, `test_simple (line 71)`, `test_damage (line 83)`, `test_duplicate (line 88)`, `test_slashes (line 96)`, `test_uppercase (line 104)`, `test_strangeletters (line 112)`. Key harness variables include `SCRIPTDIR (line 12)`, `SERVERCONFFILE (line 13)`, `NET (line 14)`, `CONFIGURATION (line 15)`, `DBWRAP_TOOL (line 16)`, `NET (line 18)`, `NETREG (line 20)`, `REGORIG (line 21)`, `REG (line 22)`, `ALLOWEDERR (line 32)`; plus 10 more.

## Control Flow
The file is 145 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 120: testit "simple" \`, `line 124: testit "damages_registry" \`, `line 128: testit "duplicate" \`, `line 132: testit "slashes" \`, `line 136: testit "uppercase" \`.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values.

## Dependencies and Integration Points
External command integrations: `net`, `grep`, `sed`, `cp`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, grep, sed, cp paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry_check.sh -->
