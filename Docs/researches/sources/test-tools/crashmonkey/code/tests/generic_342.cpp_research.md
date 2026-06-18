# sources/test-tools/crashmonkey/code/tests/generic_342.cpp

Purpose: f2fs generic/342 reproduction. It renames a 16 KiB `foo` to `bar`, creates a new 4 KiB `foo`, fsyncs new `foo`, and expects both files with their distinct sizes after recovery.

Important APIs/types/functions: `Generic342`, `WriteData`, `rename`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: setup creates `test_dir_a/foo`, writes 16 KiB, and syncs. Run renames `foo` to `bar`, creates a new `foo`, writes 4 KiB, fsyncs new `foo` through `cm_`, and checkpoints. Check stats both paths and compares sizes against `FOO_NEW_SIZE` and `FOO_OLD_SIZE`.

State/persistence behavior: the old file's data/metadata must survive under `bar`, while the new `foo` must contain only the new 4 KiB data.

Dependencies/integration: fixed `/mnt/snapshot`, f2fs bug motivation, and CrashMonkey wrappers for final file operations.

Risks/test signals: one check references `stats_old.st_size` even when `stat_foo` failed, so missing-new-file paths can be brittle. Signals include missing `bar` or wrong sizes.
