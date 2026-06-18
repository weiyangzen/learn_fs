<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_cross_node.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_cross_node.sh

## Purpose
Blackbox/selftest shell script for Samba's smbXsrv client cross node behavior. It drives the local test environment through `smbclient`, `smbstatus`, `jq`, `kill`, `sleep`, `mkfifo`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_smbXsrv_client_cross_node.sh SERVERCONFFILE NODE0 NODE1 SHARENAME`. Important routines are `test_smbclient (line 25)`, `smbstatus_num_sessions (line 50)`. Key harness variables include `CONF (line 12)`, `NODE0 (line 13)`, `NODE1 (line 14)`, `SHARE (line 15)`, `SMBCLIENT (line 17)`, `SMBSTATUS (line 18)`, `UID_WRAPPER_INITIAL_RUID (line 52)`, `CLI_FORCE_INTERACTIVE (line 63)`, `CLIENT_PID (line 72)`.

## Control Flow
The file is 92 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 25: test_smbclient()`, `line 33: subunit_start_test "$name"`, `line 37: subunit_pass_test "$name"`, `line 39: echo "$output" | subunit_fail_test "$name"`, `line 55: testit_grep "step1: smbstatus 0 sessions" '^0$' smbstatus_num_sessions || failed=$(expr $failed + 1)`, `line 57: test_smbclient "smbclient against node0[${NODE0}]" "${NODE0}" "${SHARE}" "ls" -U"${DC_USERNAME}"%"${DC_PASSWORD}" \`, `line 61: testit_grep "step2: smbstatus 0 sessions" '^0$' smbstatus_num_sessions || failed=$(expr $failed + 1)`, `line 66: testit "start backgroup smbclient against node0[${NODE0}]" true || failed=$(expr $failed + 1)`, `line 76: testit "sleep 1 second" true || failed=$(expr $failed + 1)`, `line 79: testit_grep "step3: smbstatus 1 session" '^1$' smbstatus_num_sessions || failed=$(expr $failed + 1)`; plus 2 more.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbstatus`, `jq`, `kill`, `sleep`, `mkfifo`, `rm`. Sourced/helper scripts include `. "$incdir"/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbstatus, jq, kill, sleep, mkfifo, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_cross_node.sh -->
