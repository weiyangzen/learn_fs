# sources/test-tools/crashmonkey/code/tests/generic_090.cpp

Purpose: xfstests generic/090 reproduction for append persistence with hard links. It ensures appended data fsynced after link creation survives crash recovery.

Important APIs/types/functions: `Generic090`, `WriteData`, `fsync`, `sync`, `link`, `Checkpoint`, `md5sum` via `popen`, and `DataTestResult`.

Control flow: `setup()` creates a 64 KiB `foo_backup` expected image. `run()` creates `foo`, writes 32 KiB and fsyncs it, syncs, creates a hard link, syncs again, appends/writes another 32 KiB at offset 32768, fsyncs, and checkpoints. `check_test()` compares `foo` against `foo_backup` when checkpoint 1 is reached.

State/persistence behavior: the final durable file should include both initial and appended extents despite the inode having an extra hard link.

Dependencies/integration: `mnt_dir_` paths, external `md5sum`, raw hard-link and fsync semantics.

Risks/test signals: the test assumes `WriteData` produces the same data pattern for `foo` and backup. Failure is missing file or checksum mismatch.
