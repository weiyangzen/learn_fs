<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_forceuser_validusers.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_forceuser_validusers.sh

## Purpose
Blackbox/selftest shell script for Samba's forceuser validusers behavior. It drives the local test environment through `smbclient`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_forceuser_validusers.sh SERVER DOMAIN USERNAME PASSWORD LOCAL_PATH SMBCLIENT <smbclient arguments>`. Important routines are `run_cmd_nooutput (line 29)`, `test_force_user_valid_users (line 47)`. Key harness variables include `SERVER (line 13)`, `DOMAIN (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `LOCAL_PATH (line 17)`, `SMBCLIENT (line 18)`, `SMBCLIENT (line 19)`, `ADDARGS (line 21)`, `CMD (line 31)`, `SMB_SHARE (line 49)`.

## Control Flow
The file is 60 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 54: testit "force user not works when combined with valid users" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_forceuser_validusers.sh -->
