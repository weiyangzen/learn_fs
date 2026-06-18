<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_aio_ratelimit.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_aio_ratelimit.sh

## Purpose
Blackbox/selftest shell script for Samba's aio ratelimit behavior. It drives the local test environment through `smbclient`, `sleep`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: "${SELF}" SERVERCONFFILE SMBCLIENT \`. Important routines are `test_aio_ratelimit_basic (line 32)`, `test_aio_ratelimit_burst (line 88)`, `test_aio_ratelimit_recovery (line 138)`. Key harness variables include `SELF (line 5)`, `CONF (line 13)`, `SMBCLIENT (line 14)`, `SERVER (line 15)`, `LOCAL_PATH (line 16)`, `SHARE (line 17)`, `SAMBA_DEPRECATED_SUPPRESS (line 20)`, `SECONDS (line 43)`, `CLI_FORCE_INTERACTIVE (line 46)`, `CLI_FORCE_INTERACTIVE (line 57)`; plus 10 more.

## Control Flow
The file is 208 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 196: testit "test_aio_ratelimit_basic" \`, `line 200: testit "test_aio_ratelimit_burst" \`, `line 204: testit "test_aio_ratelimit_recovery" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `sleep`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, sleep, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_aio_ratelimit.sh -->
