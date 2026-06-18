# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-7.cpp

Purpose: generated hard-link workload from a root file into directory `A`. It checks persistence of a link created in a child directory after fsyncing the original root file.

Important APIs/types/functions: `testName`, `mkdir`, `cm_->CmOpen`, raw `link`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: run creates `A`, creates root `foo`, hard-links `foo` as `A/bar`, fsyncs root `foo`, and checkpoints. The checker reinitializes paths and validates namespace expectations.

State/persistence behavior: after checkpoint 1, both names should be valid hard links to the same inode, or at least the linked child name should not be lost if the test oracle requires it.

Dependencies/integration: raw hard-link operation combined with `cm_` file fsync/checkpoint.

Risks/test signals: parent directory `A` is not fsynced after link creation, so behavior is filesystem-dependent. Main signals are missing original or linked name.
