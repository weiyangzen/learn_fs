<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry_import.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_registry_import.sh

## Purpose
Blackbox/selftest shell script for Samba's net registry import behavior. It drives the local test environment through `net`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_registry_import.sh SERVER LOCAL_PATH USERNAME PASSWORD`. Important routines are `test_net_registry_import (line 24)`. Key harness variables include `SERVER (line 10)`, `LOCAL_PATH (line 11)`, `USERNAME (line 12)`, `PASSWORD (line 13)`, `ADDARGS (line 15)`.

## Control Flow
The file is 192 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 183: testit "Test net rpc registry import" \`.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `net`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry_import.sh -->
