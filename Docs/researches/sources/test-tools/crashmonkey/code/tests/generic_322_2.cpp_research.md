# sources/test-tools/crashmonkey/code/tests/generic_322_2.cpp

Purpose: generic/322 write-after-fsync-rename variant. It tests whether data written and `sync_file_range`d before a rename is preserved when the renamed file is fsynced.

Important APIs/types/functions: `Generic322_2`, `WriteData`, `fsync`, `sync_file_range`, `rename`, `Checkpoint`, `md5sum`, and `DataTestResult`.

Control flow: setup creates `foo` and `foo_backup`, writes/fsyncs the first 4 KiB, writes another 4 KiB at offset 4096 to both, uses `sync_file_range` for `foo`, fsyncs backup, and syncs. Run renames `foo` to `bar`, fsyncs `bar`, and checkpoints. Check performs mutual-exclusion checks and md5 comparison against backup.

State/persistence behavior: both the initial fsynced data and the later range-synced data should be present in `bar` after checkpoint 1.

Dependencies/integration: Linux `sync_file_range`, external `md5sum`, and directory rename semantics.

Risks/test signals: `sync_file_range` does not provide the same metadata durability as fsync on all filesystems. Failures are missing `bar`, both names present, or checksum mismatch.
