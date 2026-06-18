# sources/test-tools/crashmonkey/code/tests/seq1/j-lang96.cpp

Purpose: ACE-generated workload that creates `A/foo`, writes 32 KiB, zeroes a keep-size range starting at byte 30,768, then issues a whole-system sync before the CrashMonkey checkpoint. It isolates zero-range persistence when global sync, rather than file or directory fsync, is the durability signal before crash-state enumeration.

Important APIs/types/functions: `BaseTestCase`, `WriteData`, `CmOpen`, `CmSync`, `CmCheckpoint`, `CmClose`, Linux `fallocate`, and the dynamic loader exports. The path fields mirror the other generated `seq1` workloads and provide a stable naming convention used by generated code.

Control flow: `setup` records mount-relative names; `run` creates directory `A`, opens `A/foo`, writes a deterministic 32 KiB range, calls `fallocate(FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE, 30768, 5000)`, calls `cm_->CmSync()`, records one checkpoint, optionally returns at checkpoint `1`, and closes the file. `check_test` performs no direct checks.

State/persistence behavior: the workload combines data writes, extent zeroing, global sync, and a checkpoint marker. The global sync becomes a `DiskMod::kSyncMod` through the wrapper, so replay logic can distinguish it from fsync/fdatasync and sync-file-range.

Dependencies/integration: requires kernel fallocate zero-range support, user-tool checkpoint IPC, and CrashMonkey diff comparison. Risks/test signals: the fallocate call is direct rather than `CmFallocate`, so wrapper metadata may not capture the range in the user-level mod list; the test is still useful when block-level logging observes the actual IO.
