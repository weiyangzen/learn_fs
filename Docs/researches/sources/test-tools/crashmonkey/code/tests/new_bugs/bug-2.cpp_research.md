# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-2.cpp

Purpose: generated workload for nested directory rename and later file rename. It moves `A/C` to `B`, creates/fsyncs `B/bar`, checkpoints, then renames `B/bar` to `A/bar` and fsyncs `A`.

Important APIs/types/functions: `testName`, `mkdir`, `cm_->CmOpen(..., O_DIRECTORY)`, `cm_->CmRename`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: setup initializes paths for `A`, `A/C`, `B`, and child file names. Run creates `A` and `A/C`, opens `A/C` as a directory, renames `A/C` to `B`, creates/fsyncs `B/bar`, checkpoints, renames `B/bar` to `A/bar`, opens/fsyncs `A`, and checkpoints again.

State/persistence behavior: recovery must preserve both directory move and later file move without duplicating or losing `bar`.

Dependencies/integration: relies on `cm_` wrappers for rename/fsync/checkpoints and raw directory creation.

Risks/test signals: complex path reuse means old `AC_*` and `B_*` names can be confused. Signals are missing `A/bar`, stale `B/bar`, or incorrect directory topology after checkpoints.
