# sources/test-tools/xfstests/tests/generic/785


Purpose: Log replay test ensuring fsyncing a parent directory after renaming an fsynced file also persists a newly created sibling directory and its entry.


Important APIs, helpers, and commands: Uses `dmflakey`, `fssum`, xfs_io pwrite/fsync, and `_scratch_sync`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_fssum`, `_require_metadata_journaling`, `_require_scratch`.
 Regression annotations include `_fixed_by_fs_commit btrfs 5630f7557de6 \`.



Control flow, state, dependencies, risks, and test signals: The script creates file1, syncs, writes/fsyncs it, creates dir/foo, renames file1 to file2, fsyncs root, records an fssum digest, simulates power failure, and validates the digest. State is file data, directory entries, and filesystem log. Dependencies are fssum, journaling, and flakey target. Risks are fssum availability and filesystem-specific metadata ordering. Signal is fssum verification success. Source size is 73 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
