<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb1_lanman_plaintext.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smb1_lanman_plaintext.sh

## Purpose
Blackbox/selftest shell script for Samba's smb1 lanman plaintext behavior. It drives the local test environment through `smbclient`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_smb1_lanman_plaintext.sh SERVER USERNAME PASSWORD`. Key harness variables include `SERVER (line 13)`, `USERNAME (line 14)`, `PASSWORD (line 15)`.

## Control Flow
The file is 63 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 27: test_smbclient "test_default" "ls" "//$SERVER/tmp" $opt || failed=$(expr $failed + 1)`, `line 37: test_smbclient_expect_failure "test_lm_fail" "ls" "//$SERVER/tmp" $opt || failed=$(expr $failed + 1)`, `line 46: test_smbclient "test_lm_ok" "ls" "//$SERVER/tmp" $opt || failed=$(expr $failed + 1)`, `line 56: test_smbclient_expect_failure "test_plaintext_fail_local" "ls" "//$SERVER/tmp" $opt || failed=$(expr $failed + 1)`, `line 59: test_smbclient "test_plaintext_ok" "ls" "//$SERVER/tmp" $opt || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`. Sourced/helper scripts include `. $incdir/subunit.sh`, `. $incdir/common_test_fns.inc`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smb1_lanman_plaintext.sh -->
