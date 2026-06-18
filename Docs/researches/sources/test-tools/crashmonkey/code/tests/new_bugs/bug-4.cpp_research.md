# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-4.cpp

Purpose: generated workload for directory rename, recreating the old directory, and fsyncing the renamed directory. It is similar to generic/341 in a smaller `A`/`B` shape.

Important APIs/types/functions: `testName`, `mkdir`, `cm_->CmRename`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: run creates `A`, checkpoints, renames `A` to `B`, creates/fsyncs `B/foo`, checkpoints, recreates `A`, creates `A/foo`, opens/fsyncs directory `B`, and checkpoints again.

State/persistence behavior: after final checkpoint, both the recreated `A` state and renamed `B` state should be represented without losing `B/foo` or confusing the old and new `A`.

Dependencies/integration: raw `mkdir`, `cm_` rename/open/fsync/checkpoint, fixed path members initialized from `mnt_dir_`.

Risks/test signals: no explicit fsync of recreated `A`; the test is designed to expose rename replay ordering gaps. Signals are missing files or stale old directory state.
