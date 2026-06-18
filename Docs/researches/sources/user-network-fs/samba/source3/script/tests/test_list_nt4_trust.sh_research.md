<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_list_nt4_trust.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_list_nt4_trust.sh

## Purpose
Blackbox/selftest shell script for Samba's list nt4 trust behavior. It drives the local test environment through `smbclient`, `wbinfo`, `sleep`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
Important routines are `test_trust_wbinfo_m (line 12)`.

## Control Flow
The file is 25 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 23: testit "nt4trust_wbinfo_m" test_trust_wbinfo_m || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`, `wbinfo`, `sleep`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, wbinfo, sleep, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_list_nt4_trust.sh -->
