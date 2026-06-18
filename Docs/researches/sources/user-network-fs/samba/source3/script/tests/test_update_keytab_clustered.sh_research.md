# sources/user-network-fs/samba/source3/script/tests/test_update_keytab_clustered.sh

Purpose: clustered variant of machine-account secret and keytab update testing. It verifies that a `clusteredmember` selftest environment can use the configured sync-machine-password hook to update node keytabs consistently when the machine password changes.

Important functions and APIs: uses Samba blackbox subunit helpers, `$BINDIR/wbinfo`, `net`, `rpcclient`, `smbclient`, and `smbcontrol`. `check_net_ads_testjoin()` and `test_keytab_create()` run `net ads` commands under `UID_WRAPPER_ROOT` to simulate root privileges. `get_biggest_vno()` parses keytab KVNOs. `test_pwd_change()` reads KVNOs from multiple node keytabs, executes a supplied password-change command, verifies `net ads testjoin`, and checks the new KVNO is synchronized.

Control flow: the script installs `source3/script/updatekeytab_test.sh` into the clustered prefix, writes `sync machine password script = ...` into `global_inject.conf`, reloads winbind, checks the initial join, performs an initial secret-change/check, creates keytabs, tests the synchronized password change, checks SMB machine login, then clears the injected configuration and reloads winbind again.

State and persistence: it mutates `global_inject.conf` for the cluster member test environment, writes keytabs below `$PREFIX/clusteredmember/node.*`, and changes the domain machine secret. The script resets the injected config at the end but relies on the surrounding selftest cleanup for environment state.

Dependencies and integration: registered from `selftest/tests.py` as `samba3.blackbox.update_keytab_clustered` and gated by the `clusteredmember` environment. It depends on CTDB-style node paths, UID wrapper behavior, and the update-keytab callout script.

Risks and test signals: there is a copy/paste-looking issue in the new node KVNO reads: all three new values are read from `node.0/keytab0`, so cross-node divergence after the change may not be detected. Strong signals are successful reloads, `net ads testjoin`, `wbinfo --check-secret`, machine-pass SMB access, and KVNO increment. The test is sensitive to cluster path layout and wrapper privileges.
