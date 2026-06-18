<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_rpcclient.sh

## Purpose
Blackbox/selftest shell script for Samba's rpcclient behavior. It drives the local test environment through `rpcclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_rpcclient.sh ccache binding <rpcclient commands>`. Key harness variables include `KRB5CCNAME (line 10)`, `ADDARGS (line 13)`.

## Control Flow
The file is 19 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 17: testit "rpcclient" $VALGRIND $BINDIR/rpcclient $ADDARGS || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
State touched or modeled by this file includes Kerberos credential caches. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `rpcclient`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes Kerberos credential caches, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rpcclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rpcclient.sh -->
