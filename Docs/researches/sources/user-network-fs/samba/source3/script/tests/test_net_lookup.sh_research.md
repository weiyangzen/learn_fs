<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_lookup.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_lookup.sh

## Purpose
Blackbox/selftest shell script for Samba's net lookup behavior. It drives the local test environment through `net`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `echo "Usage: $0 SERVER USERNAME PASSWORD NET SAMBA-TOOL DNS-ZONE"`. Key harness variables include `SERVER (line 8)`, `USERNAME (line 10)`, `PASSWORD (line 12)`, `NET (line 14)`, `SAMBATOOL (line 16)`, `DNSZONE (line 18)`, `SITE (line 21)`.

## Control Flow
The file is 54 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 36: testit_grep global 10.53.57.30:389 $NET lookup ldap "$DNSZONE" ||`, `line 40: testit_grep site-aware 1.2.3.4:389 $NET lookup ldap "$DNSZONE" "$SITE" ||`, `line 44: testit_grep global 10.53.57.30:389 $NET lookup ldap "$DNSZONE" nosite ||`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `net`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_lookup.sh -->
