# sources/user-network-fs/samba/source3/script/tests/test_veto_files.sh

Purpose: regression and behavior coverage for `veto files`, hidden-file filtering, name mangling, and per-user veto rules. It verifies clients cannot read or create paths hidden by veto rules, including within vetoed directories.

Important functions and APIs: imports `subunit.sh` and `common_test_fns.inc`; uses `smbclient` helpers plus local filesystem setup. `do_cleanup()` removes all test fixture paths. `smbclient_get_expect_error()` and `smbclient_create_expect_error()` run interactive `get`/`put` commands and match either no `NT_STATUS_` errors or a specific NT status. `test_get_veto_file()`, `test_create_veto_file()`, and `test_per_user()` compose the assertions.

Control flow: it first verifies normal and hidden file behavior on `veto_files_nohidden`, then builds a nested directory tree with vetoed names, hash2-mangled aliases, and user/group-specific files. It runs create, get, and per-user tests, then cleans the share path and temp directory.

State and persistence: creates many files and directories under the provided `SHAREPATH` and temporary smbclient input files under `$PREFIX/<scriptname>`. Cleanup is explicit but depends on successful progress to the end.

Dependencies and integration: registered as `samba3.blackbox.test_veto_files` in the `fileserver` environment. It depends on configured shares `veto_files` and `veto_files_nohidden`, hash2 mangling outputs, test users `user1` and `user2`, and group-based veto configuration.

Risks and test signals: expected mangled names are hard-coded, so mangling algorithm changes require fixture updates. The test provides strong behavior signals through exact NT status checks for top-level, nested, mangled, create, and per-user cases.
