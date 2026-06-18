# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/8

Purpose: OpenBSD kernel assertion fixture in VFS buffer memory code. Expected title is `assert "pg->wire_count == NUM" failed in vfs_biomem.c`.

Important parser APIs and patterns: `openbsdOopses` has assertion title regex `panic: kernel diagnostic assertion (.+) failed: file ".*/([^"]+)`, formatted as `assert %[1]v failed in %[2]v`. Shared dynamic replacement normalizes literal `1` inside the assertion to `NUM`.

Control flow: panic reports an assertion in `vfs_biomem.c` line 329. Stack flows through `__assert`, `buf_free_pages`, `buf_dealloc_mem`, `buf_put`, `brelse`, `vinvalbuf`, `ffs_truncate`, `ufs_rmdir`, `VOP_RMDIR`, `dounlinkat`, syscall, and `Xsyscall`. Later process-table output is retained.

State and persistence: static fixture with filesystem and process state; no mutable syzkaller state. The file path and assertion expression are the key persisted semantics.

Dependencies and integration: validates assertion title extraction, basename selection from full kernel source paths, and dynamic numeric normalization.

Risks: path handling must avoid leaking manager-specific prefixes into titles. Numeric replacement inside quoted assertions must remain stable.

Test signals: exact title with `NUM`; stack includes `buf_free_pages` and `ufs_rmdir`.
