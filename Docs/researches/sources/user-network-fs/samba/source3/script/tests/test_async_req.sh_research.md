<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_async_req.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_async_req.sh

## Purpose
Blackbox/selftest shell script for Samba's async req behavior. It drives the local test environment through shell builtins and harness helpers, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
Key harness variables include `SOCKET_WRAPPER_IPV4_NETWORK (line 8)`.

## Control Flow
The file is 14 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 11: testit "async_connect_send" $VALGRIND $BINDIR/async_connect_send_test ||`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Environment variables are part of the behavior and can affect client protocol mode, Kerberos caches, deprecated-option handling, or allocator diagnostics.

## Dependencies and Integration Points
Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_async_req.sh -->
