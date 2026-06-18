# sources/user-network-fs/samba/source3/script/tests/test_substitutions.sh

## Purpose
This script tests Samba configuration substitution expansion in share names, valid-user expressions, include files, and RPC share enumeration.

## Important APIs, Functions, and Control Flow
It accepts server, credentials, and prefix, resolves `smbclient` and `rpcclient` from `$BINDIR`, and loads `subunit.sh` plus `common_test_fns.inc`. It runs `test_smbclient` against shares `sub_dug`, `sub_dug2`, `sub_valid_users`, `sub_valid_users_domain`, and `sub_valid_users_group`. It then tests include-substitution share `${USERNAME}_share` with the real user, expects failure with `$DC_USERNAME`, and uses `testit_grep_count` around `rpcclient ... -c netshareenum` to verify share enumeration visibility.

## State, Dependencies, Integration, and Risks
No state is created. Dependencies include configured substitution-heavy shares, `$DC_USERNAME/$DC_PASSWORD`, and RPC share enumeration. A spelling typo in a test name (`Netative`) is harmless. Risks are output-string coupling for `netname:` and group/domain environment drift. Signals are smbclient success/failure and exact share count in rpcclient output.
