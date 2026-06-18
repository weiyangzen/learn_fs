# sources/test-tools/crashmonkey/code/tests/seq1/j-lang98.cpp

Purpose: ACE-generated workload that tests hole punching followed by fsync of the modified file itself. It creates `A/foo`, writes 32 KiB, punches a 32 KiB keep-size hole beyond the original write range, fsyncs `A/foo`, then records a checkpoint.

Important APIs/types/functions: `BaseTestCase`, `WriteData`, `CmOpen`, `CmFsync`, `CmCheckpoint`, `CmClose`, and direct Linux `fallocate`. Factory functions expose the class to `ClassLoader`.

Control flow: after path initialization, `run` creates `A`, opens `A/foo`, writes deterministic data, performs `FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE`, fsyncs the file descriptor, takes a checkpoint, optionally exits at checkpoint `1`, and closes the descriptor. `check_test` resets paths and returns success.

State/persistence behavior: the file fsync is the explicit persistence boundary for both data and extent metadata, followed by CrashMonkey checkpointing. This contrasts with sibling generated tests that use global sync, sibling-file fsync, or directory fsync.

Dependencies/integration: uses crash harness replay, Linux fallocate flags, and external diffing. Risks/test signals: fallocate bypasses `CmFallocate`, check logic is external, and the punched range begins at EOF for a 32 KiB file, so behavior may largely reflect allocation/metadata side effects rather than visible file bytes.
