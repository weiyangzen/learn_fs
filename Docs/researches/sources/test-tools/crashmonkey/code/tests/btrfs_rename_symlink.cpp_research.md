# sources/test-tools/crashmonkey/code/tests/btrfs_rename_symlink.cpp

Purpose: attempts to reproduce the Btrfs rename/link log-replay bug using a symlink as the original object.

Important APIs/control flow: `setup()` creates directory `A`, creates symlink `foo -> test`, and syncs. `run()` creates/fsyncs dummy, renames `foo` to `bar`, attempts to hard-link `bar` to `foo`, removes dummy, fsyncs dummy fd, checkpoints, and optionally exits.

State and persistence behavior: intended persisted state is a logged symlink rename plus recreation of the old name as a hard link. Correctness is measured by mountability/consistency.

Dependencies: POSIX symlink/rename/link behavior, Btrfs log replay, global `Checkpoint()`, and harness fsck.

Risks: class name is again `BtrfsRenameFifo`, masking the actual case. Hard-linking symlinks may follow or not follow symlinks depending on platform semantics and flags; this test uses plain `link()`. No custom namespace validation is done.

Test signals: reproduction appears through filesystem-level failure; setup/run return codes expose operation failures.
