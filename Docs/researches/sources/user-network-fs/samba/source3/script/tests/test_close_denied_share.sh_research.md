<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_close_denied_share.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_close_denied_share.sh

## Purpose
Blackbox/selftest shell script for Samba's close denied share behavior. It drives the local test environment through `smbclient`, `smbcontrol`, `sharesec`, `kill`, `sleep`, `mkfifo`; plus 2 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_close_denied_share.sh \`. Key harness variables include `CONF (line 13)`, `SHARESEC (line 14)`, `SMBCLIENT (line 15)`, `SMBCONTROL (line 16)`, `SERVER (line 17)`, `SHARE (line 18)`, `CLI_FORCE_INTERACTIVE (line 30)`, `CLIENT_PID (line 35)`, `COUNT (line 51)`, `COUNT (line 66)`.

## Control Flow
The file is 78 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 45: testit "smbcontrol" ${SMBCONTROL} ${CONF} smbd close-denied-share ${SHARE} ||`, `line 54: testit "Verify close-denied-share did not kill valid client" \`, `line 57: testit "Deny access" ${SHARESEC} ${CONF} --replace S-1-1-0:DENIED/0x0/FULL \`, `line 60: testit "smbcontrol" ${SMBCONTROL} ${CONF} smbd close-denied-share ${SHARE} ||`, `line 69: testit "Verify close-denied-share did kill now-invalid client" \`, `line 75: testit "Allow access" ${SHARESEC} ${CONF} --replace S-1-1-0:ALLOWED/0x0/FULL \`.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients, live daemon control messages. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcontrol`, `sharesec`, `kill`, `sleep`, `mkfifo`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, live daemon control messages, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcontrol, sharesec, kill, sleep, mkfifo, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_close_denied_share.sh -->
