# sources/test-tools/crashmonkey/code/tests/bug2_f2fs_fzero_fdatasync.cpp

Purpose: regression workload for an f2fs `FALLOC_FL_ZERO_RANGE | FALLOC_FL_KEEP_SIZE` recovery bug where a post-crash file size incorrectly expands to the zeroed EOF range instead of remaining at the pre-crash 16 KiB size.

Important APIs/types/functions: `F2fsFzero` derives from `BaseTestCase`; it uses `WriteData`, `syncfs`, `fallocate`, `fdatasync`, `Checkpoint`, `stat`, and `DataTestResult::kIncorrectBlockCount`/`kFileMetadataCorrupted`.

Control flow: `setup()` creates `/mnt/snapshot/test_file`, writes 8 KiB at offset 8 KiB so size becomes 16 KiB, then `syncfs()` persists it. `run()` opens the file, zero-ranges 8 KiB at offset 4,202,496 with keep-size, calls `fdatasync()`, checkpoints, and optionally stops at checkpoint 1.

State/persistence behavior: after checkpoint 1 the durable state should include extra allocated blocks but preserve `st_size == 16384`. The test specifically separates logical size from allocated block count.

Dependencies/integration: integrates Linux fallocate flags, f2fs recovery expectations, CrashMonkey checkpoint recording, and the common test plugin entry points.

Risks/test signals: hard-coded `/mnt/snapshot` and expected `st_blocks == 16` baseline can be filesystem/block-size sensitive. Failure is reported when the file is missing, size changes, or block count does not increase after `fdatasync`.
