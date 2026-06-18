<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_force_group_change.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_force_group_change.sh

## Purpose
Blackbox/selftest shell script for Samba's force group change behavior. It drives the local test environment through `smbclient`, `smbcontrol`, `rm`, `grep`, `sed`, `cp`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: test_force_group_change.sh SERVER USERNAME PASSWORD LOCAL_PATH SMBCLIENT SMBCONTROL"`. Important routines are `test_force_group_change (line 25)`. Key harness variables include `SERVER (line 12)`, `USERNAME (line 13)`, `PASSWORD (line 14)`, `LOCAL_PATH (line 15)`, `SMBCLIENT (line 16)`, `SMBCONTROL (line 17)`, `SERVER_CONFIG (line 32)`, `SERVER_CONFIG_SAVE (line 33)`, `SERVER_CONFIG_NEW (line 34)`.

## Control Flow
The file is 73 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 69: testit "test force group change" \`.

## State and Persistence Behavior
State touched or modeled by this file includes server configuration. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcontrol`, `rm`, `grep`, `sed`, `cp`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes server configuration, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcontrol, rm, grep, sed, cp paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_force_group_change.sh -->
