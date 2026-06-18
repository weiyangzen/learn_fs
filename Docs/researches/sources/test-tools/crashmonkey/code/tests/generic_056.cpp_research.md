# sources/test-tools/crashmonkey/code/tests/generic_056.cpp

Purpose: xfstests generic/056 reproduction. It ensures data fsynced to `foo` remains durable even after later namespace changes involving a hard link and another file.

Important APIs/types/functions: `Generic056`, `WriteData`, `fsync`, `Checkpoint`, `link`, `open`, `md5sum` via `popen`, and `DataTestResult::kFileDataCorrupted`.

Control flow: `setup()` creates `test_dir_a/foo`, creates `foo_backup` with the expected 4 KiB data, syncs, and closes. `run()` writes 4 KiB to `foo`, fsyncs it, checkpoints, creates a hard link, creates/fsyncs `bar`, and checkpoints again. `check_test()` verifies `foo` exists and, after checkpoint 1, matches `foo_backup` by md5.

State/persistence behavior: the first checkpoint establishes durable file data for `foo`; later link and `bar` operations must not invalidate or hide that data.

Dependencies/integration: uses `mnt_dir_` paths, external `md5sum`, and CrashMonkey checkpoints.

Risks/test signals: external command parsing is brittle. Failure is missing `foo` or checksum mismatch after a checkpoint that should have persisted data.
