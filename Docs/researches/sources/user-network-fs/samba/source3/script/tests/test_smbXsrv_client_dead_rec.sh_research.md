<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_dead_rec.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_dead_rec.sh

## Purpose
Blackbox/selftest shell script for Samba's smbXsrv client dead rec behavior. It drives the local test environment through `smbclient`, `smbstatus`, `kill`, `mkfifo`, `rm`, `grep`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_smbXsrv_client_dead_rec.sh SERVERCONFFILE IP SHARENAME`. Key harness variables include `CONF (line 12)`, `SERVER (line 13)`, `SHARE (line 14)`, `SMBCLIENT (line 16)`, `SMBSTATUS (line 17)`, `SMBD_LOG_FILE (line 19)`, `SMBD_LOG_FILE (line 21)`, `SMBD_LOG_FILE (line 23)`, `CLI_FORCE_INTERACTIVE (line 41)`, `CLIENT_PID (line 48)`; plus 1 more.

## Control Flow
The file is 76 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 73: testit "check_panic" test "$panic_count_0" -eq "$panic_count_1" ||`.

## State and Persistence Behavior
State touched or modeled by this file includes cluster client records, named pipes for interactive clients. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbstatus`, `kill`, `mkfifo`, `rm`, `grep`, `awk`. Sourced/helper scripts include `. "$incdir"/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes cluster client records, named pipes for interactive clients, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbstatus, kill, mkfifo, rm, grep, awk paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbXsrv_client_dead_rec.sh -->
