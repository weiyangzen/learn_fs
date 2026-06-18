<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_dropbox.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_dropbox.sh

## Purpose
Blackbox/selftest shell script for Samba's dropbox behavior. It drives the local test environment through `smbclient`, `chmod`, `mkdir`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER DOMAIN USERNAME PASSWORD PREFIX TARGET_ENV SMBCLIENT`. Important routines are `test_dropbox (line 30)`. Key harness variables include `SERVER (line 13)`, `DOMAIN (line 14)`, `USERNAME (line 15)`, `PASSWORD (line 16)`, `PREFIX (line 17)`, `TARGET_ENV (line 18)`, `SMBCLIENT (line 19)`, `SMBCLIENT (line 21)`, `ADDARGS (line 22)`.

## Control Flow
The file is 88 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 84: testit "dropbox dirmode 0733" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `smbclient`, `chmod`, `mkdir`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, chmod, mkdir, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_dropbox.sh -->
