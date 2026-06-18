<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb_prometheus_endpoint.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smb_prometheus_endpoint.sh

## Purpose
Blackbox/selftest shell script for Samba's smb prometheus endpoint behavior. It drives the local test environment through `smbclient`, `smbstatus`, `curl`, `kill`, `sleep`, `rm`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 SERVER SERVER_IP USERNAME PASSWORD LOCK_DIR PREFIX SMBPROMETHEUS SMBCLIENT CONFIGURATION PROTOCOL"`. Important routines are `start_smbprometheus (line 34)`, `stop_smbprometheus (line 63)`, `make_some_smb_ops (line 76)`, `test_smbprometheus_tcon (line 101)`, `test_smbprometheus_info (line 124)`, `test_smbprometheus_many (line 147)`. Key harness variables include `SERVER (line 10)`, `SERVER_IP (line 11)`, `USERNAME (line 12)`, `PASSWORD (line 13)`, `LOCK_DIR (line 14)`, `PREFIX (line 15)`, `SMBPROMETHEUS (line 16)`, `SMBCLIENT (line 17)`, `CONFIGURATION (line 18)`, `PROTOCOL (line 19)`; plus 6 more.

## Control Flow
The file is 189 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 177: testit "test_smbprometheus_tcon" \`, `line 181: testit "test_smbprometheus_info" \`, `line 185: testit "test_smbprometheus_many" \`.

## State and Persistence Behavior
State touched or modeled by this file includes profile metrics database. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbstatus`, `curl`, `kill`, `sleep`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes profile metrics database, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbstatus, curl, kill, sleep, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb_prometheus_endpoint.sh -->
