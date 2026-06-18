# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-1.cpp

Purpose: generated/new-bug namespace workload involving directories `A` and `B`, files named `foo` and `bar`, renaming `B/bar` over `A/bar`, then creating/fsyncing `A/foo`.

Important APIs/types/functions: class `testName`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmRename`, `cm_->CmCheckpoint`, raw `mkdir`, `stat`, and `DataTestResult`.

Control flow: setup initializes path strings only. Run creates `A`, creates/fsyncs `A/bar`, checkpoints, creates `B` and `B/bar`, renames `B/bar` to `A/bar`, creates `A/foo`, fsyncs `A/foo`, and checkpoints again. The comments note that an fsync of `A` may be required but is not part of the workload.

State/persistence behavior: it stresses overwrite/rename interaction with a previously fsynced file and later inode fsync in the same directory.

Dependencies/integration: heavily uses `cm_` wrappers for operations intended to be recorded, with raw `mkdir` for directory creation.

Risks/test signals: checker details are sparse and class name is generic. Expected signals are missing required names or stale overwritten names after checkpointed fsyncs.
