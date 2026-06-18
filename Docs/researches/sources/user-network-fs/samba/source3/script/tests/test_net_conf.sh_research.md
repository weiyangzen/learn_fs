<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_conf.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_net_conf.sh

## Purpose
Blackbox/selftest shell script for Samba's net conf behavior. It drives the local test environment through `net`, `rm`, `grep`, then reports pass/fail through the subunit test harness.

## Important APIs, Types, and Functions
The command contract is advertised as `Usage: test_net_conf.sh SCRIPTDIR SERVERCONFFILE NET CONFIGURATION [rpc]`. Important routines are `log_print (line 43)`, `test_conf_addshare (line 52)`, `test_conf_addshare_existing (line 160)`, `test_conf_addshare_usage (line 182)`, `test_conf_delshare (line 200)`, `test_conf_delshare_empty (line 227)`, `test_conf_delshare_usage (line 239)`, `test_conf_showshare_case (line 256)`, `test_conf_drop (line 294)`, `test_conf_drop_empty (line 322)`, `test_conf_drop_usage (line 348)`, `test_conf_setparm (line 366)`; plus 18 more. Key harness variables include `SCRIPTDIR (line 14)`, `SERVERCONFFILE (line 15)`, `NET (line 16)`, `CONFIGURATION (line 17)`, `RPC (line 18)`, `LOGDIR_PREFIX (line 20)`, `NET (line 28)`, `DIR (line 29)`, `LOG (line 30)`, `NETCMD (line 33)`; plus 9 more.

## Control Flow
The file is 1042 lines and starts with `#!/bin/sh`. Execution begins with argument/default setup, usually loads Samba's blackbox `subunit.sh` helpers, and then runs a sequence of command probes or helper functions. Observed test registrations/signals include `line 926: testit "conf_drop" \`, `line 930: testit "conf_drop_empty" \`, `line 934: testit "conf_drop_usage" \`, `line 938: testit "conf_addshare" \`, `line 942: testit "conf_addshare_existing" \`, `line 946: testit "conf_addshare_usage" \`, `line 950: testit "conf_delshare" \`, `line 954: testit "conf_delshare_empty" \`, `line 958: testit "conf_delshare_usage" \`, `line 962: testit "test_conf_showshare_case" \`; plus 18 more.

## State and Persistence Behavior
State touched or modeled by this file includes registry keys/values. Temporary files/directories are created under selftest-controlled locations and are normally removed or overwritten during cleanup.

## Dependencies and Integration Points
External command integrations: `net`, `rm`, `grep`. Sourced/helper scripts include `. $incdir/subunit.sh`. It is integrated with Samba source3 selftest conventions: positional environment arguments, `$BINDIR`/`$VALGRIND`, generated test shares, and subunit result output.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. Persistent or live state touched here includes registry keys/values, so cleanup, ordering, and parallel test isolation matter. Assertions parse human-oriented command output, so output wording and localization changes can create false failures.

## Test Signals
Primary pass/fail signals are the listed subunit/testit calls, expected nonzero failures for negative cases, and exact parsed command output. Useful regression signals include successful execution of net, rm, grep paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_net_conf.sh -->
