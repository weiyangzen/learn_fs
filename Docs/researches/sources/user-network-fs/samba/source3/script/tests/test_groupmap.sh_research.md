<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_groupmap.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_groupmap.sh

## Purpose
Blackbox/selftest shell script for Samba's groupmap behavior. It drives the local test environment through `rm`, `awk`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
Important routines are `testone (line 6)`, `tstart (line 12)`, `treport (line 17)`. Key harness variables include `TBASE (line 14)`, `TNOW (line 19)`, `TBASE (line 21)`, `NLOCAL (line 26)`, `NGROUP (line 27)`, `NBUILTIN (line 28)`, `DOMSID (line 29)`, `FORSID (line 30)`.

## Control Flow
The file is 217 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. There are no direct `testit` registrations; success is communicated by the process exit status and stdout/stderr side effects.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `rm`, `awk`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signal is the command exit status, with stdout/stderr consumed by the calling harness. Useful regression signals include successful execution of rm, awk paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_groupmap.sh -->
