## sources/sync-backup/rsync/testsuite/secure-relpath-validation_test.py

Purpose: regression test for front-door validation of relative paths passed to `secure_relative_open()`, ensuring all literal `..` components are rejected by the portable resolver path.

Important APIs and control flow: creates `SCRATCHDIR/relpath-test`, then runs the compiled helper `TOOLDIR/t_secure_relpath` with that directory. The helper owns the individual suspect-input cases and returns nonzero if any path is accepted or rejected incorrectly. The Python script fails with a concise diagnostic on nonzero return.

State and dependencies: uses `rmtree`, scratch directory creation, and a built C test helper under `TOOLDIR`.

Integration points: tests low-level secure path resolver validation used by receiver-side safe opens, especially on platforms without kernel `RESOLVE_BENEATH` equivalents.

Risks and test signals: depends on the helper being built and accurate. The signal is the helper process return code; stderr identifies the specific failing case.
