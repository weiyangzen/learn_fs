<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb1_system_security.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smb1_system_security.sh

## Purpose
Blackbox/selftest shell script for Samba's smb1 system security behavior. It drives the local test environment through `net`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 SERVER SERVER_IP USERNAME PASSWORD SMBTORTURE3 NET SHARE"`. Important routines are `smb1_system_security (line 25)`. Key harness variables include `SERVER (line 12)`, `SERVER_IP (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`, `SMBTORTURE3 (line 16)`, `NET (line 17)`, `SHARE (line 18)`.

## Control Flow
The file is 44 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 36: testit "grant SeSecurityPrivilege" $NET rpc rights grant $USERNAME SeSecurityPrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || failed=$(expr $failed + 1)`, `line 39: testit "smb1-system-security" smb1_system_security || failed=$(expr $failed + 1)`, `line 42: testit "revoke SeSecurityPrivilege" $NET rpc rights revoke $USERNAME SeSecurityPrivilege -U $USERNAME%$PASSWORD -I $SERVER_IP || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
State touched or modeled by this file includes temporary privilege grants.

## Dependencies and Integration Points
External command integrations: `net`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes temporary privilege grants, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb1_system_security.sh -->
