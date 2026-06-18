# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-9.cpp

Purpose: generated keep-size zero-range workload. It writes 4 KiB to root `foo`, zero-ranges the next 4 KiB with keep-size, fsyncs, and checkpoints.

Important APIs/types/functions: `testName`, `cm_->CmOpen`, `WriteData`, `fallocate(FALLOC_FL_ZERO_RANGE | FALLOC_FL_KEEP_SIZE)`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: run creates `foo`, writes 4096 bytes at offset 0, calls zero-range keep-size at offset 4096 for 4096 bytes, fsyncs, and checkpoints. The path initialization mirrors bug-8.

State/persistence behavior: the file should keep its original logical size while zero-range allocation metadata is handled durably. It targets the same size-vs-allocation class as the f2fs zero-range bug.

Dependencies/integration: Linux zero-range support and CrashMonkey wrapper operations.

Risks/test signals: if the checker does not inspect block count, it may only catch size expansion or file loss. Expected failure modes are incorrect size growth, missing file, or stale allocation accounting.
