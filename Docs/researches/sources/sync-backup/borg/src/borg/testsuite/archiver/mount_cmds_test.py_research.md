<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/mount_cmds_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/mount_cmds_test.py

Purpose: FUSE integration tests for `borg mount`, covering hardlinks, metadata fidelity, versions view, duplicate archive names, damaged chunks, mount filtering, and lock migration during daemonization.

Important APIs: `fuse_mount`, `cmd`, `assert_dirs_equal`, `create_test_files`, `create_src_archive`, `open_archive`, `Lock.migrate_lock`, `platform.process_alive`, xattr helpers, timestamp comparators, and capability flags for FUSE, hardlinks, symlinks, FIFOs, lchflags, and fakeroot.

Control flow: tests create repositories and archives, mount either whole repositories or selected archives, then inspect mounted paths. `test_fuse` compares extracted tree metadata and verifies stat/read/symlink/FIFO/xattr behavior. `test_fuse_versions_view` mounts with `-o versions` and checks per-file version directories. `test_fuse_allow_damaged_files` deletes a chunk and checks EIO versus zero-filled reads with `allow_damaged_files`. `test_migrate_lock_alive` monkeypatches `Lock.migrate_lock` to serialize process-liveness evidence from the background mount process.

State and persistence: creates mountpoints, archived trees, damaged repository objects, and a pickle side-channel for daemon process assertions. FUSE mount lifecycle is scoped by context managers.

Dependencies/integration: depends on FUSE implementation, OS permissions, xattrs, hardlink semantics, repository object deletion, lock migration, and local-only fork behavior. Risks include environmental flakiness, platform-specific permission checks, and global monkeypatch restoration. Test signals include filesystem metadata equality, mounted directory contents, expected `OSError(errno.EIO)`, and serialized lock assertions.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/mount_cmds_test.py -->
