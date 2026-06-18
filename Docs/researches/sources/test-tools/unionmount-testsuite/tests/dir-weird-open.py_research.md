# sources/test-tools/unionmount-testsuite/tests/dir-weird-open.py

Purpose: tests existing directory opens without `O_DIRECTORY` when create, exclusive, and truncate flags are present.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.open_file`.

Control flow: create/truncate combinations on a directory expect `EISDIR`, while `O_CREAT|O_EXCL` variants expect `EEXIST`. Each subtest validates the directory remains readable after the failed operation.

State and persistence: should not mutate the existing directory or create replacement files.

Dependencies and integration: uses `ctx.non_empty_dir`, terminal-slash mode, and open flag modeling.

Risks: errno precedence around `O_CREAT|O_EXCL` on directories is subtle and kernel-dependent.

Test signals: validates Linux VFS directory-open behavior through overlayfs copy-up paths.
