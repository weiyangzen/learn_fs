<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_durable_handle_reconnect.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_durable_handle_reconnect.sh

## Purpose
Blackbox/selftest shell script for Samba's durable handle reconnect behavior. It drives the local test environment through `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
Key harness variables include `SMBD_LOG_FILES (line 22)`, `SMBD_LOG_FILES (line 25)`.

## Control Flow
The file is 54 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 16: testit "durable_v2_delay.durable_v2_reconnect_delay" $VALGRIND \`, `line 28: testit "durable_v2_delay.durable_v2_reconnect_delay_msec" $VALGRIND \`, `line 45: testit "durable-v2-regressions.durable_v2_reconnect_bug15624" \`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `rm`. Sourced/helper scripts include `. $(dirname $0)/../../../testprogs/blackbox/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_durable_handle_reconnect.sh -->
