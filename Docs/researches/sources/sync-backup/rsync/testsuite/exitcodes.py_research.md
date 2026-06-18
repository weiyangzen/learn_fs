## sources/sync-backup/rsync/testsuite/exitcodes.py

Purpose: centralizes autotools-style test exit codes for the Python testsuite.

Important APIs and control flow: defines `Exit(enum.IntEnum)` with `PASS=0`, `FAIL=1`, `ERROR=2`, `SKIP=77`, and `XFAIL=78`. It has no import-time side effects by design, allowing `runtests.py` and `rsyncfns.py` to import it without triggering environment validation.

State and dependencies: depends only on the standard `enum` module and persists no state.

Integration points: re-exported by `rsyncfns` and consumed by tests through helper functions such as `test_fail`, `test_skipped`, and `test_xfail`. It is part of the contract between executable test scripts and the runner.

Risks and test signals: risk is low but changes are compatibility-sensitive because numeric values are conventional. The absence of side effects is itself important test infrastructure behavior.
