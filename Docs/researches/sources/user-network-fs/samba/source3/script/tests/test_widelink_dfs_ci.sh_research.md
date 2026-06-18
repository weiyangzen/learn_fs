# sources/user-network-fs/samba/source3/script/tests/test_widelink_dfs_ci.sh

Purpose: regression test that a DFS share with wide links enabled remains case-insensitive for normal directory operations.

Important functions and APIs: uses forced-interactive `smbclient`, subunit, and common blackbox helpers. `test_ci()` writes commands to create directory `x`, change into uppercase `X`, return, remove `x`, and quit, then checks for absence of `NT_STATUS_`.

Control flow: after suppressing deprecated option warnings, the script runs the single case-insensitivity scenario against `//SERVER/msdfs-share-wl`, using the supplied `SERVER_IP`, credentials, prefix, and extra smbclient args.

State and persistence: creates and removes directory `x` on the target DFS share. Temporary command file lives under `$PREFIX`.

Dependencies and integration: registered in `selftest/tests.py` as `samba3.blackbox.widelink_dfs_ci` in the `fileserver` environment. It depends on share `msdfs-share-wl` and the wide-links/DFS configuration being active.

Risks and test signals: the `SHARE` argument is parsed but the UNC is hard-coded to `msdfs-share-wl`, so callers cannot vary the share without editing the script. Passing signal is a successful smbclient run with no NT status errors during uppercase `cd`.
