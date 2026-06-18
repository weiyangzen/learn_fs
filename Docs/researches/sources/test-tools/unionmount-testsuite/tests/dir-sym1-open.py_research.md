# sources/test-tools/unionmount-testsuite/tests/dir-sym1-open.py

Purpose: verifies open behavior through a direct symlink to an existing directory.

Important APIs/types/functions: five `subtest_*` functions using `ctx.direct_dir_sym` and `ctx.open_file`.

Control flow: read-only open through the symlink succeeds. Write-only, append, read/write, and append/read-write opens through the symlink expect `EISDIR`, with successful read-only rechecks after each failure.

State and persistence: no intended mutation; symlink and target directory should remain lower-visible and readable.

Dependencies and integration: depends on setup-created direct directory symlink and context symlink pathwalk behavior.

Risks: terminal slash and symlink following semantics are subtle; the test assumes normal Linux following for final symlink in `open`.

Test signals: catches overlayfs regressions where directory symlink opens produce wrong errors or alter the target.
