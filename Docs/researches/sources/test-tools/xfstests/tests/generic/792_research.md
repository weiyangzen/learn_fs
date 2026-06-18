# sources/test-tools/xfstests/tests/generic/792


Purpose: Log replay test for fsyncing a directory file descriptor after rmdir of an empty directory, ensuring deletion persists after crash.


Important APIs, helpers, and commands: Uses dmflakey, xfs_io fsync, helper `unlink-fsync`, chmod/mv setup, and recursive listing filters.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`, `_require_test_program`.
 Regression annotations include `_fixed_by_fs_commit btrfs xxxxxxxxxxxx \`.



Control flow, state, dependencies, risks, and test signals: It creates dir1/dir2 and dir3, syncs, chmod/fsyncs dir1, moves dir2 into dir3, runs helper to open dir1, rmdir it, fsync the open fd, then crashes/remounts and lists contents. State is removed directory log state and moved child directory. Dependencies are helper binary, journaling, and flakey target. Risks are open-unlinked directory semantics and replay ordering. Signal is dir1 absent and dir3/dir2 present. Source size is 69 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
