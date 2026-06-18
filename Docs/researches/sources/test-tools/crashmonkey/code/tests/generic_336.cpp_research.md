# sources/test-tools/crashmonkey/code/tests/generic_336.cpp

Purpose: btrfs generic/336 reproduction. It removes a hard link in `B`, renames `B/bar` to `C/bar`, fsyncs `A/foo`, and expects the renamed file not to be lost.

Important APIs/types/functions: `Generic336`, `link`, `unlink`, `rename`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, `opendir`/`readdir`, and `DataTestResult`.

Control flow: setup creates directories `A`, `B`, `C`, file `A/foo`, hard link `B/foo_link`, file `B/bar`, and syncs. Run unlinks `B/foo_link`, renames `B/bar` to `C/bar`, opens/fsyncs `A/foo` through `cm_`, and checkpoints. Check verifies `bar` is only in `C`, `foo` remains in `A`, and `B` is empty.

State/persistence behavior: replay of fsync on the linked inode must not lose unrelated renamed `bar` or resurrect removed link state.

Dependencies/integration: mixes raw namespace operations with `cm_` wrappers for the final fsync/checkpoint.

Risks/test signals: a source typo checks `stat_new_res_bar` against `foo_path_moved` in similar files, but this file's check is mostly explicit. Signals are missing bar, duplicate bar, missing foo, or nonempty `B`.
