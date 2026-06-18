<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/access.c -->
## sources/test-tools/strace/tests/access.c

Purpose: Tests pathname and mode decoding for the `access` syscall, including SELinux context decoration when enabled.

Important APIs/types/functions: Uses `__NR_access`, `create_and_enter_subdir`, `SECONTEXT_PID_MY`, `SECONTEXT_FILE`, `open`, `unlink`, and `leave_and_remove_subdir`.

Control flow: Enters a subdirectory so tracer and tracee cwd differ, creates `access_sample`, calls `access(sample, F_OK)`, removes it, then calls `access(sample, R_OK|W_OK|X_OK)` and prints expected decoded lines.

State and persistence: Temporarily creates `access_subdir/access_sample` and removes both.

Dependencies and integration: Depends on `secontext.h` and common test helpers. Its output interacts with path decoding and SELinux-aware expected formatting.

Risks: File permission semantics and SELinux context availability vary by environment. Cleanup failures can affect later tests in the same directory.

Test signals: Expected output should include `F_OK`, combined `R_OK|W_OK|X_OK`, optional file contexts, and a clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/access.c -->
