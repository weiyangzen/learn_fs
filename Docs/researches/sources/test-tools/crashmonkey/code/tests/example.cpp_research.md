# sources/test-tools/crashmonkey/code/tests/example.cpp

Purpose: minimal example of a CrashMonkey workload using the `cm_` filesystem wrapper rather than raw syscalls for key operations. It creates `A/foo`, then creates `B`, hard-links `A/foo` into `B/foo`, fsyncs the source file, and checkpoints.

Important APIs/types/functions: `Example`, `BaseTestCase`, `cm_->CmFsync`, `cm_->CmCheckpoint`, raw `mkdir`, `open`, `link`, `sync`, `stat`, and plugin entry points `test_case_get_instance`/`test_case_delete_instance`.

Control flow: `setup()` builds directory `A`, creates `A/foo`, and globally syncs. `run()` creates `B`, creates a hard link from `A/foo` to `B/foo`, fsyncs the original file through the CrashMonkey wrapper, checkpoints, and returns at checkpoint 1. `check_test()` stats both paths.

State/persistence behavior: after the checkpoint, both the original and linked names are expected to resolve to a file. The workload targets link persistence through fsync of one inode.

Dependencies/integration: demonstrates interaction with `RecordCmFsOps`/`PassthroughCmFsOps` selected by `BaseTestCase::Run`.

Risks/test signals: the directory creation and link call are raw syscalls, so only wrapper-covered operations are recorded in the same way as other `cm_` workloads. Missing `A/foo` or `B/foo` is the main signal.
