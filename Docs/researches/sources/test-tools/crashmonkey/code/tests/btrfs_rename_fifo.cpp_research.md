# sources/test-tools/crashmonkey/code/tests/btrfs_rename_fifo.cpp

Purpose: reproduces a Btrfs log-replay bug involving a FIFO that is renamed and hard-linked under the old name before crash.

Important APIs/control flow: `setup()` creates directory `A`, creates FIFO `foo` with `mkfifo()`, and syncs. `run()` creates/fsyncs a dummy file, renames `foo` to `bar`, links `bar` to `foo`, removes dummy, fsyncs the dummy fd, checkpoints, and optionally exits. `check_test()` performs no custom validation.

State and persistence behavior: correct behavior is that the replayed filesystem remains mountable/consistent after the logged FIFO rename/link sequence.

Dependencies: POSIX FIFO, rename/link/fsync, global `Checkpoint()`, Btrfs log replay, and harness fsck/mount checks.

Risks: hard-linking a FIFO may behave differently across filesystems and permissions. `fd_dummy` can leak on checkpoint return. The test relies exclusively on filesystem-level signals.

Test signals: failure is expected as mount/fsck/checker error, not data-test error.
