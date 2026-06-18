<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_registry_upgrade.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_registry_upgrade.sh

## Purpose
Blackbox/selftest shell script for Samba's registry upgrade behavior. It drives the local test environment through `net`, `mkdir`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: test_registry_upgrade.sh NET DBWRAP_TOOL"`. Important routines are `registry_check (line 35)`, `registry_upgrade (line 78)`. Key harness variables include `SCRIPT_DIR (line 12)`, `BASE_DIR (line 13)`, `NET (line 15)`, `DBWRAP_TOOL (line 16)`, `DATADIR (line 17)`, `WORKSPACE (line 18)`, `CONFIG_FILE (line 19)`, `CONFIGURATION (line 20)`, `NETCMD (line 22)`, `REGPATH (line 31)`; plus 12 more.

## Control Flow
The file is 192 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 186: testit "registry_upgrade" registry_upgrade || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values, server configuration. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `net`, `mkdir`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, server configuration, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, mkdir, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_registry_upgrade.sh -->
