<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_tdb.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_tdb.sh

## Purpose
Blackbox/selftest shell script for Samba's net tdb behavior. It drives the local test environment through `smbclient`, `net`, `tdbtool`, `kill`, `sleep`, `touch`; plus 3 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SMBCLIENT SERVER SHARE USER PASS CONFIGURATION LOCALPATH LOCKDIR`. Key harness variables include `SMBCLIENT (line 19)`, `SERVER (line 20)`, `SHARE (line 21)`, `USER (line 22)`, `PASS (line 23)`, `CONFIGURATION (line 24)`, `LOCALPATH (line 25)`, `LOCKDIR (line 26)`, `FILENAME (line 28)`, `SMBCLIENTPID (line 45)`; plus 2 more.

## Control Flow
The file is 121 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 50: testit "Looking for record key of open file" \`, `line 80: testit "Looking for open file in locking.tdb" \`, `line 87: testit "Verify pathname in output" \`, `line 93: testit "Verify filename in output" \`, `line 100: testit "Verify number of share modes in output" \`, `line 104: testit "Complete record dump" \`, `line 110: testit "Verify filename in dump output" \`, `line 115: testit "Verify share path in dump output" \`.

## State and Persistence Behavior
State touched or modeled by this file includes TDB lock records.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `tdbtool`, `kill`, `sleep`, `touch`, `grep`, `awk`, `sed`. Sourced/helper scripts include `# shellcheck source=testprogs/blackbox/subunit.sh`, `. "$incdir/subunit.sh"`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes TDB lock records, so cleanup, ordering, and parallel test isolation matter. Several checks are timing-sensitive because they coordinate background clients, daemon reload/control messages, FIFOs, sleeps, or cluster state. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, tdbtool, kill, sleep, touch, grep, awk paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_tdb.sh -->
