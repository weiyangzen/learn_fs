<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_sacl_set_get.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_sacl_set_get.sh

## Purpose
Blackbox/selftest shell script for Samba's sacl set get behavior. It drives the local test environment through `net`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 SERVER SERVER_IP USERNAME PASSWORD SMBTORTURE3 NET SHARE"`. Important routines are `sacl_set_get (line 26)`. Key harness variables include `SERVER (line 13)`, `SERVER_IP (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `SMBTORTURE3 (line 17)`, `NET (line 18)`, `SHARE (line 19)`.

## Control Flow
The file is 45 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 37: testit "grant SeSecurityPrivilege" $NET rpc rights grant $USERNAME SeSecurityPrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || failed=$(expr $failed + 1)`, `line 40: testit "SACL set_get" sacl_set_get || failed=$(expr $failed + 1)`, `line 43: testit "revoke SeSecurityPrivilege" $NET rpc rights revoke $USERNAME SeSecurityPrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
State touched or modeled by this file includes temporary privilege grants.

## Dependencies and Integration Points
External command integrations: `net`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes temporary privilege grants, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_sacl_set_get.sh -->
