<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_chdir_cache.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_chdir_cache.sh

## Purpose
Blackbox/selftest shell script for Samba's chdir cache behavior. It drives the local test environment through `smbclient`, `smbcontrol`, `kill`, `sleep`, `mkfifo`, `rm`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: test_chdir_cache.sh \`. Key harness variables include `CONF (line 16)`, `SMBCLIENT (line 18)`, `SMBCONTROL (line 20)`, `SERVER (line 22)`, `SHARE (line 24)`, `PREFIX (line 26)`, `TESTENV (line 28)`, `SAMBA_DEPRECATED_SUPPRESS (line 32)`, `CLI_FORCE_INTERACTIVE (line 50)`, `CLIENT_PID (line 55)`.

## Control Flow
The file is 120 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 91: testit "reload config 1" \`, `line 108: testit "reload config 2" \`, `line 117: testit "Verify we got at least one chdir error" \`.

## State and Persistence Behavior
State touched or modeled by this file includes named pipes for interactive clients. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcontrol`, `kill`, `sleep`, `mkfifo`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes named pipes for interactive clients, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcontrol, kill, sleep, mkfifo, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_chdir_cache.sh -->
