# sources/test-tools/crashmonkey/code/tests/btrfs_rename_dev.cpp

Purpose: attempts to reproduce a Btrfs log-replay unmountable-filesystem bug involving renaming a device special file and hard-linking it back to the old name.

Important APIs/control flow: `setup()` creates directory `A`, then calls `mknod()` for `foo` with special-file bits, syncs, and returns. `run()` creates and fsyncs a dummy file to populate the log tree, renames `foo` to `bar`, links `bar` back to `foo`, removes the dummy file, fsyncs the dummy fd, checkpoints, and optionally exits.

State and persistence behavior: baseline contains a special file; workload logs rename/link operations in one transaction and uses dummy-file fsync/removal to persist the log tree. Correct behavior is mountable recovery.

Dependencies: root privileges for `mknod`, POSIX rename/link/fsync, Btrfs log-tree behavior, global `Checkpoint()`.

Risks: class name is `BtrfsRenameFifo` despite device-file semantics, suggesting copy/paste confusion. `S_IFCHR | S_IFBLK` combines mutually exclusive file-type bits and may make `mknod()` invalid. The code fsyncs `fd_dummy` after removing the path, which may be intentional but is subtle. No custom check validates recovered namespace.

Test signals: harness mount/fsck failures indicate reproduction; setup can fail early if `mknod()` is not permitted or invalid.
