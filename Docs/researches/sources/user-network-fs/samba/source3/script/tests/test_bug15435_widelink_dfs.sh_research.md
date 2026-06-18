<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_bug15435_widelink_dfs.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_bug15435_widelink_dfs.sh

## Purpose
Blackbox/selftest shell script for Samba's bug15435 widelink dfs behavior. It drives the local test environment through `smbclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_bug15435_widelink_dfs.sh SERVER SERVER_IP USERNAME PASSWORD SMBCLIENT CONFIGURATION <smbclient arguments>`. Key harness variables include `SERVER (line 12)`, `SERVER_IP (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`, `CONFIGURATION (line 17)`, `ADDARGS (line 19)`.

## Control Flow
The file is 28 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 26: test_smbclient "smbclient as $DOMAIN\\$USERNAME" 'ls' "//$SERVER/msdfs-share-wl" -U$DOMAIN\\$USERNAME%$PASSWORD $ADDARGS -c 'cd msdfs-src1' || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_bug15435_widelink_dfs.sh -->
