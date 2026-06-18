<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_recycle.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_recycle.sh

## Purpose
Blackbox/selftest shell script for Samba's recycle behavior. It drives the local test environment through `smbclient`, `sleep`, `ln`, `chmod`, `rm`, `touch`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_recycle.sh SERVER SERVER_IP USERNAME PASSWORD LOCAL_PATH PREFIX SMBCLIENT ADDARGS`. Important routines are `do_cleanup (line 38)`, `test_recycle (line 82)`, `test_touch (line 121)`, `test_recycle_crossrename (line 154)`. Key harness variables include `SERVER (line 10)`, `SERVER_IP (line 11)`, `USERNAME (line 12)`, `PASSWORD (line 13)`, `LOCAL_PATH (line 14)`, `PREFIX (line 15)`, `SMBCLIENT (line 16)`, `SMBCLIENT (line 17)`, `ADDARGS (line 19)`, `SAMBA_DEPRECATED_SUPPRESS (line 27)`; plus 2 more.

## Control Flow
The file is 223 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 201: testit "recycle" \`, `line 205: testit "recycle_touch" \`, `line 209: testit "recycle_crossrename" \`, `line 215: testit "check_panic" test $panic_count_0 -eq $panic_count_1 || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `sleep`, `ln`, `chmod`, `rm`, `touch`, `grep`. Sourced/helper scripts include `. "$incdir"/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, sleep, ln, chmod, rm, touch, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_recycle.sh -->
