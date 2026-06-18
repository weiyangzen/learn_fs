# sources/test-tools/unionmount-testsuite/tests/dir-open-dir.py

Purpose: verifies opening existing populated directories with `O_DIRECTORY` across read and write access modes.

Important APIs/types/functions: six `subtest_*` functions calling `ctx.open_dir`.

Control flow: each subtest chooses `ctx.non_empty_dir()` with optional terminal slash, opens it read-only successfully, or attempts write-only, append, read/write, and append/read-write forms expecting `EISDIR`, then reopens read-only to confirm the directory remains accessible.

State and persistence: no intended mutation; all operations should preserve the lower directory and its contents.

Dependencies and integration: depends on setup-created populated directories and `context.open_dir` flag/error handling.

Risks: expected errno can vary for unusual filesystems, especially with terminal slashes or non-overlay direct mode.

Test signals: confirms directory opens do not copy up or corrupt directories and that write-like open modes are rejected.
