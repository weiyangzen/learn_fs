<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_force_close_share.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_force_close_share.sh

## Purpose
Blackbox/selftest shell script for Samba's force close share behavior. It drives the local test environment through `smbclient`, `smbcontrol`, `kill`, `sleep`, `mkfifo`, `mkdir`; plus 2 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: $0 SERVERCONFFILE SMBCLIENT SMBCONTROL IP aio_delay_inject_sharename PREFIX`. Key harness variables include `CONFIGURATION (line 17)`, `SMBCONTROL (line 19)`, `SERVER (line 20)`, `SHARE (line 21)`, `PREFIX (line 22)`, `SAMBA_DEPRECATED_SUPPRESS (line 26)`, `FIFO_STDIN (line 37)`, `FIFO_STDOUT (line 38)`, `FIFO_STDERR (line 39)`, `TESTFILE (line 40)`; plus 3 more.

## Control Flow
The file is 115 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 89: testit "smbcontrol" ${SMBCONTROL} ${CONFIGURATION} smbd close-share ${SHARE} ||`, `line 105: testit "Verify close-share did cancel the file put" \`, `line 111: test_smbclient "remove_testfile" \`.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients, live daemon control messages. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcontrol`, `kill`, `sleep`, `mkfifo`, `mkdir`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, live daemon control messages, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcontrol, kill, sleep, mkfifo, mkdir, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_force_close_share.sh -->
