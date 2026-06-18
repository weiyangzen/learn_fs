# sources/test-tools/crashmonkey/code/tests/generic_041.cpp

Purpose: xfstests generic/041 reproduction for btrfs hard-link/extref replay. It creates thousands of hard links, mutates link names, fsyncs the inode, and checks directory cleanup after crash recovery.

Important APIs/types/functions: `Generic041`, `link`, `remove`, `fsync`, `Checkpoint`, `rmdir`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: `setup()` creates `test_dir_a/foo`, creates links `foo_link_0` through `foo_link_2999`, syncs, and closes. `run()` removes `foo_link_0`, creates `foo_link_3000`, recreates `foo_link_0`, fsyncs `foo`, and checkpoints. `check_test()` removes all entries and attempts `rmdir`.

State/persistence behavior: durable inode reference tracking must survive conversion between regular refs and extended refs. Replay must not leave unremovable stale link metadata.

Dependencies/integration: direct POSIX workload with a high link count; relies on filesystem hard-link limits and btrfs historical behavior for motivation.

Risks/test signals: setup is expensive and may exceed link-count limits on some filesystems. The signal is directory cleanup failure after all visible entries are removed.
