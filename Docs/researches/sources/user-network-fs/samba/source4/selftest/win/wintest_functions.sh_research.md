# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_functions.sh

Purpose: shared shell functions for Windows VM setup, cleanup, and snapshot recovery.

Important functions: `setup_share_test()` builds a temporary expect script from `common.exp` and `wintest_setup.exp`, runs it, stores status in global `err_rtn`, and removes the temp file. `remove_share_test()` does the same for `wintest_remove.exp`. `restore_snapshot()` prints a failure message and invokes `vmrun revertToSnapshot`, either locally or with `-h/-P/-u/-p` host credentials.

State and dependencies: global variables from `test_win.conf` drive paths, credentials, and VMX location. The functions mutate the Windows VM by creating/removing shares and reverting snapshots.

Risks and test signals: temporary filenames are fixed per `$TMPDIR`, so concurrent tests can collide. Arguments are mostly unquoted. `restore_snapshot()` reports success/failure but does not return a hard failure to callers beyond `err_rtn`.
