# sources/sync-backup/rsync/testsuite/chmod-option_test.py

Purpose: tests client `--chmod` transforms and daemon `incoming chmod`, including a historical directory misclassification bug.

Important APIs/types/functions: `check_perms`, `checkit`, `check_permcopy`, `build_rsyncd_conf`, `start_test_daemon`, `run_rsync`, and mode manipulation with `os.chmod`/`os.umask`.

Control flow: build a source with varied modes, copy it to `checkdir`, set umask 002, manually apply the expected `ug-s,a+rX,D+w` transform to `checkdir`, and compare rsync output with that expected tree. It then tests chmod permission-copy expressions (`g=o,o=`, `g=u`, `g-o`, etc.), verifies invalid `g=ur` is rejected, checks `Fo-x` file-only chmod, and pushes with `--no-perms` to a daemon module with `incoming chmod = Fo-x`.

State and persistence behavior: deliberately leaves umask at 002 for consistent transform semantics. Destination modes are the main persistent state.

Dependencies and integration points: chmod parser, receiver mode-setting logic, daemon incoming chmod handling, and harness permissions checks.

Risks and test signals: mode semantics depend on umask and platform permission behavior. Failures reveal parser mistakes, wrong F/D scoping, or daemon directory/file misclassification.
