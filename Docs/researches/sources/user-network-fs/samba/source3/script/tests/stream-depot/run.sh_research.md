<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/stream-depot/run.sh -->
# sources/user-network-fs/samba/source3/script/tests/stream-depot/run.sh

## Purpose
Runs the stream-depot VFS `vfstest` scenario in a temporary directory to validate named-stream storage behavior.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: run.sh VFSTEST PREFIX`. Key harness variables include `TESTBASE (line 9)`, `VFSTEST (line 10)`, `PREFIX (line 11)`, `ADDARGS (line 13)`, `VFSTEST_PREFIX (line 15)`, `VFSTEST_TMPDIR (line 16)`, `NUM (line 28)`.

## Control Flow
The file is 36 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 25: testit "vfstest" $VFSTEST -f $TESTBASE/vfstest.cmd $ADDARGS || failed=$(expr $failed + 1)`, `line 27: subunit_start_test $testname`, `line 30: echo "streams_depot left ${NUM} in .streams, expected 3" | subunit_fail_test $testname`, `line 33: subunit_pass_test $testname`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `vfstest`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of vfstest paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/stream-depot/run.sh -->
