<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_printing_var_exp.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_printing_var_exp.sh

## Purpose
Blackbox/selftest shell script for Samba's printing var exp behavior. It drives the local test environment through `smbclient`, `rpcclient`, `sleep`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_printing_var_exp.sh SERVER SERVER_IP DOMAIN USERNAME PASSWORD`. Important routines are `test_var_expansion (line 25)`, `test_empty_queue (line 58)`. Key harness variables include `SERVER (line 10)`, `SERVER_IP (line 11)`, `DOMAIN (line 12)`, `USERNAME (line 13)`, `PASSWORD (line 14)`, `ADDARGS (line 16)`, `JOBS (line 64)`.

## Control Flow
The file is 93 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 85: testit "Test variable expansion for '%U', '%u' and '%D'" \`, `line 89: testit "Test queue is empty" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rpcclient`, `sleep`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rpcclient, sleep, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_printing_var_exp.sh -->
