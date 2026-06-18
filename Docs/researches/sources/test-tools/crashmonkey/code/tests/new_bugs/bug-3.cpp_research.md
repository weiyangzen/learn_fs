# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-3.cpp

Purpose: generated workload mixing separate fsync epochs, hard-link creation, and parent directory fsync. It creates files in `B`, links `B/foo` into `A/C/foo`, and fsyncs `A`.

Important APIs/types/functions: `testName`, `mkdir`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, raw `link`, and `DataTestResult`.

Control flow: run creates `A`, `A/C`, and `B`; creates/fsyncs `B/foo` and checkpoints; creates/fsyncs `B/bar` and checkpoints; hard-links `B/foo` to `A/C/foo`; opens/fsyncs directory `A`; and checkpoints a third time.

State/persistence behavior: after final checkpoint, the link into the nested directory and the existing `B` files should be consistent. It probes whether fsyncing a parent captures child-directory link changes.

Dependencies/integration: raw hard-link call plus `cm_` file/directory fsyncs.

Risks/test signals: parent `A` fsync may not durably cover `A/C` changes on all filesystems, making the oracle intentionally aggressive. Failures likely include missing link or stale namespace state.
