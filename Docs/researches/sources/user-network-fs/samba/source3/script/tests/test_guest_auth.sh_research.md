<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_guest_auth.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_guest_auth.sh

## Purpose
Blackbox/selftest shell script for Samba's guest auth behavior. It drives the local test environment through `smbclient`, `net`, `smbcontrol`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER SMBCLIENT SMBCONTROL NET CONFIGURATION`. Important routines are `prepare_empty_builtin_guests (line 27)`, `add_local_guest_to_builtin_guests (line 54)`, `test_smbclient (line 64)`. Key harness variables include `SERVER (line 15)`, `SMBCLIENT (line 16)`, `SMBCONTROL (line 17)`, `NET (line 18)`, `CONFIGURATION (line 19)`, `SIDS (line 25)`, `TMP (line 29)`, `SIDS (line 36)`.

## Control Flow
The file is 106 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 64: test_smbclient()`, `line 74: testit "smbclient_guest_at_startup" \`, `line 75: test_smbclient ||`, `line 90: testit "smbclient_guest_auth_without_members" \`, `line 91: test_smbclient ||`, `line 102: testit "smbclient_works_after_restored_setup" \`, `line 103: test_smbclient ||`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `smbcontrol`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, smbcontrol paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_guest_auth.sh -->
