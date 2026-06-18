# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-10.cpp

Purpose: reduced directory rename workload. It creates `A`, checkpoints, renames `A` to `B`, creates/fsyncs `B/foo`, and checkpoints again.

Important APIs/types/functions: `testName`, `mkdir`, `cm_->CmRename`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: setup initializes root, `A`, `B`, and child paths. Run creates `A`, checkpoints, renames `A` to `B`, creates `B/foo`, fsyncs that file, and checkpoints. The checker reinitializes paths and validates the recovered namespace.

State/persistence behavior: after the second checkpoint, `B/foo` should exist and the old `A` location should not reappear as an independent directory unless recovery legitimately stopped before the rename checkpoint.

Dependencies/integration: raw `mkdir` plus `cm_` rename/open/fsync/checkpoint wrappers.

Risks/test signals: no parent directory fsync is performed, so the workload intentionally probes whether file fsync captures enough rename context. Signals are missing new directory/file or stale old directory.
