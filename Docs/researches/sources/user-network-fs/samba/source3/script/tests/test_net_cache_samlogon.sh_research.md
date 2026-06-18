<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_cache_samlogon.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_cache_samlogon.sh

## Purpose
Blackbox/selftest shell script for Samba's net cache samlogon behavior. It drives the local test environment through `smbclient`, `net`, `grep`, `awk`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER SHARE USER PASS`. Key harness variables include `SERVER (line 13)`, `SHARE (line 14)`, `USER (line 15)`, `PASS (line 16)`.

## Control Flow
The file is 43 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 26: test_smbclient "Prime samlogon cache" 'exit' //$SERVER/$SHARE -U$USER%$PASS || failed=$(expr $failed + 1)`, `line 29: testit "net cache samlogon list" $BINDIR/net cache samlogon list || failed=$(expr $failed + 1)`, `line 34: testit "net cache samlogon show $usersid" $BINDIR/net cache samlogon show $usersid || failed=$(expr $failed + 1)`, `line 36: testit "net cache samlogon show SID name matches name from list command" test x"$tmp" = x"$username" || failed=$(expr $failed + 1)`, `line 38: testit "net cache samlogon ndrdump $usersid" $BINDIR/net cache samlogon ndrdump $usersid || failed=$(expr $failed + 1)`, `line 41: testit "net cache samlogon ndrdump returns netr_SamInfo3 structure" test $retval -eq 0 || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `grep`, `awk`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, grep, awk paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_cache_samlogon.sh -->
