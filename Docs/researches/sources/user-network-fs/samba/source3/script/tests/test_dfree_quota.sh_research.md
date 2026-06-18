<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_dfree_quota.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_dfree_quota.sh

## Purpose
Blackbox/selftest shell script for Samba's dfree quota behavior. It drives the local test environment through `smbclient`, `smbcacls`, `smbcquotas`, `kill`, `sleep`, `mkdir`; plus 4 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_dfree_quota.sh SERVER DOMAIN USERNAME PASSWORD LOCAL_PATH SMBCLIENT SMBCQUOTAS SMBCACLS`. Important routines are `sighup_smbd (line 31)`, `conf_lines (line 36)`, `setup_1_conf (line 88)`, `setup_conf (line 97)`, `test_smbclient_dfree (line 112)`, `test_smbclient_dfree_2 (line 144)`, `test_smbcquotas (line 174)`. Key harness variables include `SERVER (line 13)`, `DOMAIN (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `ENVDIR (line 17)`, `WORKDIR (line 18)`, `CONFFILE (line 26)`.

## Control Flow
The file is 303 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 112: test_smbclient_dfree()`, `line 123: subunit_start_test "$name"`, `line 130: subunit_pass_test "$name"`, `line 133: echo "$output" | subunit_fail_test "$name"`, `line 137: echo "$output" | subunit_fail_test "$name"`, `line 144: test_smbclient_dfree_2()`, `line 152: subunit_start_test "$name"`, `line 162: subunit_pass_test "$name"`, `line 165: echo "$output" | subunit_fail_test "$name"`, `line 169: echo "$output" | subunit_fail_test "$name"`; plus 28 more.

## State and Persistence Behavior
State touched or modeled by this file includes fake quota database/configuration, fake disk-free configuration, running smbd process signaling. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcacls`, `smbcquotas`, `kill`, `sleep`, `mkdir`, `rm`, `touch`, `awk`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes fake quota database/configuration, fake disk-free configuration, running smbd process signaling, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcacls, smbcquotas, kill, sleep, mkdir, rm, touch paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_dfree_quota.sh -->
