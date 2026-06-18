# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-5.cpp

Purpose: generated hard-link and multi-file workload. It creates `A/foo`, links it as `B/foo`, fsyncs the original, then creates `A/bar`, opens `B/foo`, fsyncs the linked name, and checkpoints.

Important APIs/types/functions: `testName`, `mkdir`, raw `link`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: run creates `A` and `B`, creates `A/foo`, hard-links it to `B/foo`, fsyncs `A/foo`, checkpoints, creates `A/bar`, opens `B/foo`, fsyncs `B/foo`, and checkpoints again.

State/persistence behavior: the same inode is referenced from two directories and fsynced through both names at different times. Recovery should preserve the link relationship and the later `A/bar` creation according to checkpoint.

Dependencies/integration: raw hard-link operation and `cm_` wrapper fsync/checkpoint operations.

Risks/test signals: the checker must distinguish two names for one inode from duplicate independent files. Expected failures are missing link target, stale/missing `bar`, or bad namespace placement.
