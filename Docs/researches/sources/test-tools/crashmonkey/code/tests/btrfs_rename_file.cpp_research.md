# sources/test-tools/crashmonkey/code/tests/btrfs_rename_file.cpp

Purpose: control-style test for the same rename/link/fsync sequence using a regular file, documented as not expected to fail.

Important APIs/control flow: `setup()` creates directory `A`, creates regular file `foo`, syncs, and closes it. `run()` creates/fsyncs dummy, renames `foo` to `bar`, hard-links `bar` to `foo`, removes dummy, fsyncs dummy fd, checkpoints, and optionally exits.

State and persistence behavior: baseline has a regular file. After replay, the filesystem should remain mountable and consistent; no custom data checks are performed.

Dependencies: POSIX file APIs, global `Checkpoint()`, Btrfs or other filesystem recovery behavior.

Risks: comments refer to "FIFO" in setup despite regular-file code. The test does not validate that both names exist or have expected link counts after recovery. `fd_dummy` can leak on early checkpoint return.

Test signals: successful mount/fsck with no data errors is the expected control signal.
