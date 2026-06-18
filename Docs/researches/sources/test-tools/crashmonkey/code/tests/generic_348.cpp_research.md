# sources/test-tools/crashmonkey/code/tests/generic_348.cpp

Purpose: btrfs generic/348 symlink replay regression. It verifies that symlink targets are not recovered as empty strings after fsyncing the symlink parent directories.

Important APIs/types/functions: `Generic348`, `symlink`, `mkdir`, `open`, `fsync`, `Checkpoint`, `readlink`, `PATH_MAX`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: setup creates and syncs directory `A`. Run creates symlink `A/bar1 -> /mnt/snapshot/foo1`, fsyncs `A`, creates directory `B`, creates symlink `B/bar2 -> /mnt/snapshot/foo2`, fsyncs `B`, and checkpoints. Check reads both symlinks and verifies target strings are non-empty.

State/persistence behavior: after checkpoint 1, symlink inodes and their target payloads should be durable for both an already-persisted parent and a newly-created parent.

Dependencies/integration: fixed `/mnt/snapshot` paths and POSIX symlink/readlink behavior.

Risks/test signals: `ReadLink` returns the literal `"readlink error"` on failure, which is non-empty and can mask missing symlinks. The explicit signal only catches empty recovered targets.
