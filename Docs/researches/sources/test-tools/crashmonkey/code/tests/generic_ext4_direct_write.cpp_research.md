# sources/test-tools/crashmonkey/code/tests/generic_ext4_direct_write.cpp

Purpose: ext4 direct-write regression workload. It combines a delayed buffered write that extends i_size with a direct synchronous write to the first block, then checks recovered size/block metadata consistency.

Important APIs/types/functions: `genericDirectWrite`, `cm_->CmOpen`, `WriteData`, `O_DIRECT`, `O_SYNC`, `posix_memalign`, `pwrite`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: setup creates an empty durable `test_file`. Run opens it normally through `cm_`, writes 4 KiB at offset 16 KiB buffered, closes, reopens with `O_DIRECT | O_SYNC`, writes an aligned 4 KiB buffer at offset 0, sleeps, checkpoints without fsyncing the buffered write, and closes.

State/persistence behavior: if blocks are allocated after recovery, i_size must not be zero. The workload targets ext4 ordering where direct write block allocation could persist while i_size stayed stale.

Dependencies/integration: requires direct-I/O alignment, `posix_memalign`, and CrashMonkey wrapper operations.

Risks/test signals: intentionally avoids fsync because it would hide the bug, so the oracle is metadata consistency rather than full data durability. Failure is `st_blocks > 0 && st_size == 0`.
