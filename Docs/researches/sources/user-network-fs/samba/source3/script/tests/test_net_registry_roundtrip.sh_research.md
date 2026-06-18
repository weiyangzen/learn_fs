<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry_roundtrip.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_registry_roundtrip.sh

## Purpose
Blackbox/selftest shell script for Samba's net registry roundtrip behavior. It drives the local test environment through `net`, `rm`, `grep`, `sed`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_registry_roundtrip.sh SCRIPTDIR SERVERCONFFILE NET CONFIGURATION RPC`. Important routines are `conf_roundtrip_step (line 48)`, `conf_roundtrip (line 63)`. Key harness variables include `SCRIPTDIR (line 15)`, `SERVERCONFFILE (line 16)`, `NET (line 17)`, `CONFIGURATION (line 18)`, `RPC (line 19)`, `NET (line 21)`, `NETCMD (line 24)`, `NETCMD (line 26)`, `SED_INVALID_PARAMS (line 38)`, `REGPATH (line 46)`; plus 5 more.

## Control Flow
The file is 158 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 153: testit "conf_roundtrip $conf_file" \`.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `net`, `rm`, `grep`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, rm, grep, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_registry_roundtrip.sh -->
