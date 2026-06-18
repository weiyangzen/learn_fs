# sources/test-tools/crashmonkey/code/tests/generic_341.cpp

Purpose: btrfs generic/341 reproduction for directory rename and recreation. It renames `A/X` to `A/Y`, recreates an empty `A/X`, fsyncs the new `X`, and checks that old contents moved to `Y`.

Important APIs/types/functions: `Generic341`, `WriteData`, `rename`, `mkdir`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: setup creates `A/X` with `foo` and `bar`, writes 8 KiB to each, and syncs. Run renames `X` to `Y`, creates a new `X`, fsyncs the new directory through `cm_`, and checkpoints. Check stats old and moved paths for `foo` and `bar`.

State/persistence behavior: after recovery, the recreated `X` should be empty and `Y` should contain both original files. Files should not be missing or present in both directories.

Dependencies/integration: fixed `/mnt/snapshot`, raw rename/mkdir, and `cm_` wrapped fsync/checkpoint.

Risks/test signals: the check for `bar`'s new path appears to stat `foo_path_moved` instead of `bar_path_moved`, weakening bar-specific detection. Missing or duplicate moved files are reported.
