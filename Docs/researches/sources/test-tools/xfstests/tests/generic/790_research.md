# sources/test-tools/xfstests/tests/generic/790


Purpose: Log replay test for replacing a persisted directory with a file of the same name while adding directories and hardlinks before parent fsync.


Important APIs, helpers, and commands: Uses dmflakey, xfs_io directory fsync, recursive ls filtering, and `_scratch_sync`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`.
 Regression annotations include `_fixed_by_fs_commit btrfs 9573a365ff9f \`.



Control flow, state, dependencies, risks, and test signals: The test persists `foo` as a directory, removes it, creates dir1/dir2, creates file `foo`, hardlinks it into dir2, fsyncs dir2 and root, crashes/remounts, and lists expected contents. State is name-type conflict history, hardlink metadata, and log. Dependencies are journaling and flakey. Risks are replay ordering around conflicting inodes. Signals are post-crash listing containing dir1, dir2/link, and file foo. Source size is 70 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
