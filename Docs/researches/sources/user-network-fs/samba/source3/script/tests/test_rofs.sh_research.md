<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rofs.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_rofs.sh

## Purpose
Blackbox/selftest shell script for Samba's rofs behavior. It drives the local test environment through `smbclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo Usage: $0 SERVERCONFFILE SMBCLIENT SERVER SHARE`. Key harness variables include `CONF (line 10)`, `SMBCLIENT (line 12)`, `SERVER (line 14)`, `SHARE (line 16)`.

## Control Flow
The file is 34 lines and starts with `#!/usr/bin/env bash`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 29: testit_grep "Expect MEDIA_WRITE_PROTECTED" NT_STATUS_MEDIA_WRITE_PROTECTED \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_rofs.sh -->
