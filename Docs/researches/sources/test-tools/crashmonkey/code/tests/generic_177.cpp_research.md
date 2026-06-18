# sources/test-tools/crashmonkey/code/tests/generic_177.cpp

Purpose: xfstests generic/177 reproduction for multiple overlapping hole punches. It checks that a sequence of punched ranges persists exactly after fsync and crash recovery.

Important APIs/types/functions: `Generic177`, `WriteData`, `fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)`, `fsync`, `Checkpoint`, `md5sum`, and `DataTestResult`.

Control flow: `setup()` builds `foo_backup` by writing 128 KiB, syncing, applying three hole punches, syncing, and closing. `run()` creates `foo`, writes 128 KiB, fsyncs, applies the same three hole punches, fsyncs again, and checkpoints. `check_test()` compares `foo` to `foo_backup` by md5 after checkpoint 1.

State/persistence behavior: durable state should include holes at 96-128 KiB, 64-192 KiB, and roughly 32-128 KiB according to the source offsets, with unchanged data elsewhere.

Dependencies/integration: Linux fallocate punch support and external `md5sum`.

Risks/test signals: one offset is `32786`, not a clean 32 KiB boundary, which may be intentional or a typo; it changes the exact expected image. Failure is checksum mismatch.
