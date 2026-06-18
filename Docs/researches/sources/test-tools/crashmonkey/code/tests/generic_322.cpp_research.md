# sources/test-tools/crashmonkey/code/tests/generic_322.cpp

Purpose: xfstests generic/322 rename-data test. It renames a data-containing `foo` to `bar`, fsyncs `bar`, and expects `bar` to exist with the original data after recovery.

Important APIs/types/functions: `Generic322`, `WriteData`, `rename`, `open`, `fsync`, `Checkpoint`, `md5sum` via `popen`, `stat/open` checks, and `DataTestResult`.

Control flow: setup creates `test_dir_a/foo` and `foo_backup`, writes matching 4 KiB data to both, syncs, and closes. Run renames `foo` to `bar`, opens/fsyncs `bar`, and checkpoints. Check ensures old and new names are mutually exclusive, requires `bar` after checkpoint 1, and compares `bar` to backup.

State/persistence behavior: the rename and file contents must both survive; having both names or neither name is invalid.

Dependencies/integration: direct POSIX operations, external `md5sum`, and CrashMonkey checkpointing.

Risks/test signals: checksum helper assumes `md5sum` output is available and parseable. Signals are old file persisted, file missing, or data checksum mismatch.
