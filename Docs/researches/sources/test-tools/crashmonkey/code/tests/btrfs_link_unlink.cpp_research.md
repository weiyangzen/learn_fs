# sources/test-tools/crashmonkey/code/tests/btrfs_link_unlink.cpp

Purpose: reproduces a Btrfs 4.16 bug where unlinking and recreating a hard-link name followed by fsync can leave the filesystem unmountable after crash.

Important APIs/control flow: `setup()` creates directory `A`, file `foo`, hard link `bar`, syncs, and closes `foo`. `run()` unlinks `bar`, recreates it as a new file, fsyncs `bar`, checkpoints, and optionally exits at checkpoint 1. `check_test()` returns clean and relies on harness fsck/mount results.

State and persistence behavior: baseline has two links to `foo`; workload changes `bar` from hard link to separate file and fsyncs it. Crash-state correctness is primarily filesystem mountability/consistency.

Dependencies: POSIX `link`, `unlink`, `open`, `fsync`, global `Checkpoint()`, Btrfs recovery behavior, and `BaseTestCase`.

Risks: uses direct POSIX and global `Checkpoint()` rather than `cm_` wrappers, so user-tool modification recording may be less complete. `fd_bar` is not closed before returning checkpoint `1`. No custom data validation checks link counts or file identity after recovery.

Test signals: expected failure appears as kernel mount/fsck failure in `FileSystemTestResult`, not `DataTestResult`.
