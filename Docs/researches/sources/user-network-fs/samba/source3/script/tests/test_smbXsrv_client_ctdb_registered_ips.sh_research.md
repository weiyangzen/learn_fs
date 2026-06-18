<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_ctdb_registered_ips.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_ctdb_registered_ips.sh

## Purpose
Blackbox/selftest shell script for Samba's smbXsrv client ctdb registered ips behavior. It drives the local test environment through `smbclient`, `smbstatus`, `ctdb`, `jq`, `kill`, `sleep`; plus 2 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_smbXsrv_client_ctdb_registered_ips.sh SERVERCONFFILE CTDB_IFACE_IP SHARENAME`. Important routines are `test_smbclient (line 26)`, `smbstatus_num_sessions (line 53)`, `ctdb_add_public_ip (line 59)`, `ctdb_ip (line 65)`, `ctdb_gettickles (line 70)`, `ctdb_reload_public_ips (line 75)`. Key harness variables include `CONF (line 12)`, `CTDB_IFACE_IP (line 13)`, `SHARE (line 14)`, `SMBCLIENT (line 16)`, `SMBSTATUS (line 17)`, `CTDB (line 18)`, `TIMELIMIT (line 19)`, `UID_WRAPPER_INITIAL_RUID (line 56)`, `UID_WRAPPER_INITIAL_RUID (line 61)`, `UID_WRAPPER_INITIAL_RUID (line 62)`; plus 7 more.

## Control Flow
The file is 159 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 26: test_smbclient()`, `line 34: subunit_start_test "$name"`, `line 38: subunit_pass_test "$name"`, `line 40: echo "$output" | subunit_fail_test "$name"`, `line 81: testit_grep_count "step1: smbstatus 0 sessions" '^0$' 1 smbstatus_num_sessions || failed=$(expr $failed + 1)`, `line 83: test_smbclient "step2: smbclient against node0[${CTDB_IFACE_IP}]" "${CTDB_IFACE_IP}" "${SHARE}" "ls" -U"${DC_USERNAME}"%"${DC_PASSWORD}" \`, `line 87: testit_grep_count "step2: smbstatus 0 sessions" '^0$' 1 smbstatus_num_sessions || failed=$(expr $failed + 1)`, `line 92: testit "step3: start backgroup smbclient against node0[${CTDB_IFACE_IP}]" true || failed=$(expr $failed + 1)`, `line 102: testit_grep_count "step3: smbclient1-stdout" 'Try "help" to get a list of possible commands.' 1 $TIMELIMIT 15 head -1 smbclient1-stdout || failed=$(expr $failed + 1)`, `line 104: testit_grep_count "step3: smbstatus 1 session" '^1$' 1 smbstatus_num_sessions || failed=$(expr $failed + 1)`; plus 21 more.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients, cluster public IP/tickle state. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbstatus`, `ctdb`, `jq`, `kill`, `sleep`, `mkfifo`, `rm`. Sourced/helper scripts include `. "$incdir"/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, cluster public IP/tickle state, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbstatus, ctdb, jq, kill, sleep, mkfifo, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_ctdb_registered_ips.sh -->
