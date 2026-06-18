<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_aio_outstanding.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_aio_outstanding.sh

## Purpose
Blackbox/selftest shell script for Samba's aio outstanding behavior. It drives the local test environment through `smbclient`, `kill`, `sleep`, `mkfifo`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_aio_outstanding.sh \`. Key harness variables include `CONF (line 16)`, `SMBCLIENT (line 17)`, `SERVER (line 18)`, `SHARE (line 19)`, `SAMBA_DEPRECATED_SUPPRESS (line 22)`, `CLI_FORCE_INTERACTIVE (line 45)`, `CLIENT_PID (line 50)`.

## Control Flow
The file is 99 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 96: testit "check_panic" test $panic_count_0 -eq $panic_count_1 ||`.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `kill`, `sleep`, `mkfifo`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, kill, sleep, mkfifo, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_aio_outstanding.sh -->
