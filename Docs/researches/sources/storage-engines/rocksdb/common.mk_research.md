# sources/storage-engines/rocksdb/common.mk

## Purpose
Shared Makefile fragment for Python selection and test temporary-directory setup across RocksDB make targets.

## Important APIs and Control Flow
If `PYTHON` is undefined, it chooses `python3`, then `python`, then literal `python3`, and exports the result. For temporary directories, `TEST_TMPDIR` falls back from `TMPD`, then `BASE_TMPDIR`, then `TMPDIR`, then `/tmp`. If no explicit test tmp dir exists, it prefers `/dev/shm` only when it has the sticky bit, then creates a random `rocksdb.XXXX` directory with Perl `File::Temp` and `CLEANUP => 0`.

## State, Dependencies, and Risks
This fragment persists environment variables for child make commands and creates a real filesystem directory used by tests/tools. Risks include dependency on Perl, unremoved temp directories because cleanup is disabled, and `/dev/shm` capacity/permission surprises. It integrates with `crash_test.mk` and other make targets that use `TEST_TMPDIR`.
