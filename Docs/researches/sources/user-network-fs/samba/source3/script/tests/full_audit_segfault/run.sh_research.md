<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/full_audit_segfault/run.sh -->
# sources/user-network-fs/samba/source3/script/tests/full_audit_segfault/run.sh

## Purpose
Runs a `vfstest` command file under a TALLOC free-fill setting to exercise the full_audit VFS regression path that previously segfaulted.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: run.sh VFSTEST`. Key harness variables include `TALLOC_FILL_FREE (line 9)`, `TESTBASE (line 12)`, `VFSTEST (line 13)`, `ADDARGS (line 15)`.

## Control Flow
The file is 25 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 22: testit "vfstest" "$VFSTEST" -f "$TESTBASE/vfstest.cmd" "$ADDARGS" ||`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
External command integrations: `vfstest`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of vfstest paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/full_audit_segfault/run.sh -->
