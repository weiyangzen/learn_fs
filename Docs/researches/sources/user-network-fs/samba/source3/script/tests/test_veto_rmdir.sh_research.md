# sources/user-network-fs/samba/source3/script/tests/test_veto_rmdir.sh

Purpose: covers directory removal semantics when directories contain vetoed files, including the `delete veto files` behavior and interaction with DFS links.

Important functions and APIs: uses forced-interactive `smbclient` with hand-written command files. `test_veto_nodelete_rmdir()` operates against the `veto_files_nodelete` share and expects `NT_STATUS_DIRECTORY_NOT_EMPTY` while a vetoed file remains. `test_veto_delete_rmdir()` operates against `veto_files_delete` and expects removal to succeed after a visible DFS symlink is removed.

Control flow: each helper creates `$SHAREPATH/dir`, a vetoed file, and an `msdfs:` symlink. It lists the directory to confirm only `dfs_link` is visible, removes the DFS link, then attempts `rd dir` and checks the expected outcome. The top-level script runs the nodelete case, cleans, runs the delete case, and cleans again.

State and persistence: creates and removes `dir`, the veto file, DFS symlink, and temporary smbclient input under `$PREFIX`. It mutates only the supplied test share path.

Dependencies and integration: registered in `selftest/tests.py` as `samba3.blackbox.test_veto_rmdir` under `fileserver`. It depends on share definitions for `veto_files_nodelete` and `veto_files_delete`, DFS symlink interpretation, and the client/server returning stable NT status strings.

Risks and test signals: the test assumes only the DFS link is visible before removal; changes to listing behavior or veto visibility can produce false failures. Good signals are the exact presence or absence of `NT_STATUS_DIRECTORY_NOT_EMPTY` and no generic `NT_STATUS_` errors in the delete-enabled case.
