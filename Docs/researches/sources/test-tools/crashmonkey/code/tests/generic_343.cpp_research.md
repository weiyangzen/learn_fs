# sources/test-tools/crashmonkey/code/tests/generic_343.cpp

Purpose: btrfs generic/343 reproduction. It combines hard-link creation, moving a directory from `Y` to `X`, moving `foo_2` from `Y` to `X`, and fsyncing `X/foo`.

Important APIs/types/functions: `Generic343`, `mkdir`, `open`, `link`, `rename`, `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, `opendir`/`readdir`, and `DataTestResult`.

Control flow: setup creates `X`, `Y`, `X/foo`, `Y/Z`, and `Y/foo_2`, then syncs. Run links `X/foo` to `X/bar`, renames `Y/Z` into `X/Z`, renames `Y/foo_2` into `X/foo_2`, fsyncs `X/foo`, and checkpoints. Check verifies `X` contains `foo`, `bar`, `foo_2`, and `Z`, while `Y` no longer contains moved entries.

State/persistence behavior: replay must not duplicate moved entries in both directories or lose them entirely. The fsynced file's log must correctly carry related directory operations.

Dependencies/integration: raw namespace operations plus `cm_` final fsync/checkpoint.

Risks/test signals: check variable `empty_B` is unused legacy naming. Signals are missing moved file/dir or old entries persisting in `Y`.
