<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_acl_xattr.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_acl_xattr.sh

## Purpose
Blackbox/selftest shell script for Samba's acl xattr behavior. It drives the local test environment through `smbclient`, `smbcacls`, `rm`, `touch`, `grep`, `awk`; plus 1 more, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: $0 SERVER USERNAME PASSWORD PREFIX SMBCLIENT SMBCACLS`. Important routines are `setup_remote_file (line 26)`, `smbcacls_x (line 37)`, `nt_affects_posix (line 54)`, `nt_affects_chown (line 75)`, `nt_affects_chgrp (line 110)`. Key harness variables include `SERVER (line 12)`, `USERNAME (line 13)`, `PASSWORD (line 14)`, `PREFIX (line 15)`, `SMBCLIENT (line 16)`, `SMBCACLS (line 17)`, `ADDARGS (line 19)`, `SMBCLIENT (line 20)`, `SMBCACLS (line 21)`.

## Control Flow
The file is 156 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 144: testit "setup remote file tmp" setup_remote_file tmp`, `line 145: testit "setup remote file ign_sysacls" setup_remote_file ign_sysacls`, `line 146: testit "smbcacls -x" smbcacls_x tmp`, `line 147: testit "nt_affects_posix tmp" nt_affects_posix tmp "true"`, `line 148: testit "nt_affects_posix ign_sysacls" nt_affects_posix ign_sysacls "false"`, `line 149: testit "setup remote file tmp" setup_remote_file tmp`, `line 150: testit "setup remote file ign_sysacls" setup_remote_file ign_sysacls`, `line 151: testit "nt_affects_chown tmp" nt_affects_chown tmp`, `line 152: testit "nt_affects_chown ign_sysacls" nt_affects_chown ign_sysacls`, `line 153: testit "setup remote file tmp" setup_remote_file tmp`; plus 3 more.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `smbcacls`, `rm`, `touch`, `grep`, `awk`, `sed`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, smbcacls, rm, touch, grep, awk, sed paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_acl_xattr.sh -->
