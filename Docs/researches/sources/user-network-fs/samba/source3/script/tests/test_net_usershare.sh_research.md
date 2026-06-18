<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_usershare.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_usershare.sh

## Purpose
Blackbox/selftest shell script for Samba's net usershare behavior. It drives the local test environment through `smbclient`, `net`, `mkdir`, `rm`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_usershare.sh SERVER SERVER_IP DOMAIN USERNAME PASSWORD SMBCLIENT <smbclient arguments>`. Important routines are `test_smbclient (line 30)`, `test_net_usershare (line 47)`. Key harness variables include `SERVER (line 10)`, `SERVER_IP (line 11)`, `USERNAME (line 12)`, `PASSWORD (line 13)`, `ADDARGS (line 16)`.

## Control Flow
The file is 83 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 30: test_smbclient()`, `line 71: testit "create usershare dir for $samba_usershare_name" mkdir --mode=0755 --verbose $samba_usershare_path || failed=$(expr $failed + 1)`, `line 77: test_smbclient "smbclient to $samba_usershare_name" "$samba_usershare_name" 'ls' -U$USERNAME%$PASSWORD || failed=$(expr $failed + 1)`, `line 81: testit "remove usershare dir for $samba_usershare_name" rm -rf $samba_usershare_path || failed=$(expr $failed + 1)`.

## State and Persistence Behavior
State touched or modeled by this file includes live daemon control messages. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `smbclient`, `net`, `mkdir`, `rm`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes live daemon control messages, so cleanup, ordering, and parallel test isolation matter.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of smbclient, net, mkdir, rm paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_usershare.sh -->
