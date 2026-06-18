<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_registry_share.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_registry_share.sh

## Purpose
Blackbox/selftest shell script for Samba's registry share behavior. It drives the local test environment through `smbclient`, `rpcclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_registry_share.sh SERVER USERNAME PASSWORD`. Key harness variables include `SERVER (line 12)`, `USERNAME (line 13)`, `PASSWORD (line 14)`.

## Control Flow
The file is 39 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 26: test_smbclient \`, `line 31: testit_grep_count \`.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rpcclient`. Sourced/helper scripts include `. $samba_srcdir/testprogs/blackbox/subunit.sh`, `. $samba_srcdir/testprogs/blackbox/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rpcclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_registry_share.sh -->
