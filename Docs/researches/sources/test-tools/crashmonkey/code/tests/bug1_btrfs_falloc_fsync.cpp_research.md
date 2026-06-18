# sources/test-tools/crashmonkey/code/tests/bug1_btrfs_falloc_fsync.cpp

Purpose: reproduces a Btrfs fallocate/fsync bug where keep-size allocations or zero ranges beyond EOF are lost after crash despite a subsequent fsync.

Important APIs/control flow: `setup()` creates `/mnt/snapshot/foo`, writes 16 KiB with `WriteData()`, fsyncs, syncs, and closes. `run()` opens `foo` and performs six variants: three `FALLOC_FL_KEEP_SIZE` allocations and three `FALLOC_FL_ZERO_RANGE | FALLOC_FL_KEEP_SIZE` operations at different offsets/lengths. Each variant fsyncs, checkpoints, and can stop at its checkpoint. `check_test()` stats `foo` and compares `st_blocks` against checkpoint-specific thresholds, setting `kIncorrectBlockCount` when blocks are too low.

State and persistence behavior: baseline file size remains 16 KiB, but allocated block count should increase after each beyond-EOF allocation/zero. The test uses block count as the persistence signal, not file size/data bytes.

Dependencies: Linux `fallocate()`, Btrfs behavior, CrashMonkey `Checkpoint()`, `WriteData()`, POSIX stat, and fixed mount path `/mnt/snapshot`.

Risks: expected block thresholds are noted as ext4 counts while comments say other filesystems use slightly different values; this can make cross-filesystem use noisy. `foo_path` ignores injected `mnt_dir_` and hard-codes `/mnt/snapshot`. Checkpoint returns are inconsistent: variants 1-5 return `0`, variant 6 returns `1`, which affects harness last-checkpoint logic. Open fd can leak on checkpoint returns.

Test signals: data-test error `incorrect_block_count` with a checkpoint-specific description indicates the bug. Missing file is reported as `kFileMissing`.
