# sources/user-network-fs/samba/source3/script/tests/test_update_keytab.sh

Purpose: blackbox regression coverage for AD member machine-account password rotation and keytab synchronization in the `ad_member_idmap_nss` selftest environment. It validates that `wbinfo --change-secret`, `rpcclient change_trust_pw`, `net rpc changetrustpw`, and `net ads changetrustpw` all leave generated keytabs usable and structurally correct.

Important functions and APIs: the script imports Samba blackbox `subunit.sh` and `common_test_fns.inc`, then wraps `$BINDIR/wbinfo`, `net`, `rpcclient`, and `smbclient`. `get_biggest_vno()` parses `net ads keytab list` output and stores the highest KVNO in global `vno`. `compare_keytabs_sync_kvno()` normalizes MIT and Heimdal enctype names and removes KVNOs before diffing, while `compare_keytabs_nosync_kvno()` preserves KVNO order for entries that should not sync KVNOs. `test_pwd_change()` drives a password change command, checks `net ads testjoin`, verifies KVNO increment, exports current keytabs, and compares them with static templates.

Control flow: after argument parsing and static keytab fixture definitions, the script creates a temporary keytab template directory under `$PREFIX/ad_member_idmap_nss`, deletes any existing test keytabs, performs an initial secret change/check to create old password history, creates/syncs keytabs with `net ads keytab create`, then runs the four password-change paths. It finally checks machine-pass SMB access before and after the password-change sequence.

State and persistence: persistent effects are machine account secret updates in the AD/member state, keytab files under `$PREFIX/ad_member_idmap_nss`, and temporary normalized comparison files under `TMPDIR`. Cleanup removes only `TMPDIR`; regenerated keytabs remain as part of the test environment state.

Dependencies and integration: depends on AD member provisioning variables (`DOMAIN`, `REALM`, `DC_SERVER`, `PREFIX`, `BINDIR`, `CONFIGURATION`) and selftest registration from `source3/selftest/tests.py` as `samba3.blackbox.update_keytab`. It is tightly integrated with Samba keytab generation semantics and with MIT/Heimdal output formats.

Risks and test signals: the large embedded expected-output fixtures are fragile when principals, casing, enctype policy, or keytab list formatting changes. Good signals are exact diff success after each password-change path, KVNO increment by one, successful `wbinfo --check-secret`, and `smbclient --machine-pass` access. Failures print command output and diff data, which is useful for identifying keytab drift.
