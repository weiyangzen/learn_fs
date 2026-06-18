# sources/test-tools/crashmonkey/code/tests/generic_059.cpp

Purpose: btrfs generic/059 punch-hole regression. It writes and fsyncs a 16 KiB file, punches a 4 KiB hole, fsyncs again, and expects the hole to be visible after recovery.

Important APIs/types/functions: `Generic059`, `WriteData`, `fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)`, `fsync`, `Checkpoint`, `fread`, `strlen`, `memcmp`, and `DataTestResult`.

Control flow: `setup()` creates `foo`, writes 16 KiB, fsyncs, stores the original bytes in `text`, syncs, and closes. `run()` punches 4 KiB at offset 8000, fsyncs, and checkpoints. `check_test()` reads 16 KiB and verifies the content differs from the original full-data state after checkpoint 1.

State/persistence behavior: the punched region should read as zeros after the second fsync. Seeing the original full buffer implies the punch-hole operation was lost.

Dependencies/integration: fixed `/mnt/snapshot/foo`, Linux fallocate punch flags, and CrashMonkey checkpointing.

Risks/test signals: using `strlen` on binary-ish data can be imprecise because punched holes introduce NULs by design. The robust signal is `memcmp` still matching the original buffer.
