<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_auth.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_auth.sh

## Purpose
Blackbox/selftest shell script for Samba's smbclient auth behavior. It drives the local test environment through `smbclient`, `grep`, `sed`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_smbclient_auth.sh SERVER SERVER_IP USERNAME PASSWORD SMBCLIENT <smbclient arguments>`. Key harness variables include `SERVER (line 12)`, `SERVER_IP (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`, `SMBCLIENT (line 16)`, `SMBCLIENT (line 17)`, `ADDARGS (line 19)`, `IPV6LITERAL (line 31)`.

## Control Flow
The file is 47 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 7: Usage: test_smbclient_auth.sh SERVER SERVER_IP USERNAME PASSWORD SMBCLIENT <smbclient arguments>`, `line 32: testit "smbclient //${IPV6LITERAL}/tmpguest as user" $SMBCLIENT //${IPV6LITERAL}/tmpguest $CONFIGURATION -U$USERNAME%$PASSWORD -c quit $ADDARGS || failed=$(expr $failed +`, `line 33: testit "smbclient //${IPV6LITERAL}./tmpguest as user" $SMBCLIENT //${IPV6LITERAL}./tmpguest $CONFIGURATION -U$USERNAME%$PASSWORD -c quit $ADDARGS || failed=$(expr $failed`, `line 35: testit "smbclient //${SERVER_IP}/tmpguest as user" $SMBCLIENT //${SERVER_IP}/tmpguest $CONFIGURATION -U$USERNAME%$PASSWORD -p 139 -c quit $ADDARGS || failed=$(expr $faile`, `line 37: testit "smbclient //$SERVER/guestonly as user" $SMBCLIENT //$SERVER/guestonly $CONFIGURATION -U$USERNAME%$PASSWORD -I $SERVER_IP -p 139 -c quit $ADDARGS || failed=$(expr `, `line 38: testit "smbclient //$SERVER/guestonly as anon" $SMBCLIENT //$SERVER/guestonly $CONFIGURATION -U% -I $SERVER_IP -p 139 -c quit $ADDARGS || failed=$(expr $failed + 1)`, `line 39: testit "smbclient //$SERVER/tmpguest as user" $SMBCLIENT //$SERVER/tmpguest $CONFIGURATION -U$USERNAME%$PASSWORD -I $SERVER_IP -p 139 -c quit $ADDARGS || failed=$(expr $f`, `line 40: testit "smbclient //$SERVER/tmpguest as anon" $SMBCLIENT //$SERVER/tmpguest $CONFIGURATION -U% -I $SERVER_IP -p 139 -c quit $ADDARGS || failed=$(expr $failed + 1)`, `line 41: testit "smbclient //$SERVER/forceuser as user" $SMBCLIENT //$SERVER/forceuser $CONFIGURATION -U$USERNAME%$PASSWORD -I $SERVER_IP -p 139 -c quit $ADDARGS || failed=$(expr `, `line 42: testit "smbclient //$SERVER/forceuser as anon" $SMBCLIENT //$SERVER/forceuser $CONFIGURATION -U% -I $SERVER_IP -p 139 -c quit $ADDARGS || failed=$(expr $failed + 1)`; plus 4 more.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`, `grep`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, grep, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_auth.sh -->
