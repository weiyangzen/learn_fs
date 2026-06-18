# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-6.cpp

Purpose: generated workload involving root-level and directory-level files. It creates `foo` at the mount root and `A/foo`, fsyncs `A/foo`, then creates `A/bar` and fsyncs the mount root directory.

Important APIs/types/functions: `testName`, `mkdir`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, directory `O_DIRECTORY`, and `DataTestResult`.

Control flow: run creates `A`, creates root `foo`, creates `A/foo`, fsyncs `A/foo`, checkpoints, creates `A/bar`, opens the mount root as a directory, fsyncs it, and checkpoints again.

State/persistence behavior: the workload probes whether root-directory fsync captures creation inside a child directory and how root-level and child names coexist after replay.

Dependencies/integration: `cm_` wrappers for opens/fsyncs/checkpoints, raw `mkdir`, and initialized path members.

Risks/test signals: fsyncing the root may not imply persistence of `A/bar` on all filesystems, making this an aggressive crash oracle. Signals are missing root/child files or inconsistent directory contents.
