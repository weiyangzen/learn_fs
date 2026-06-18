# sources/test-tools/xfstests/tests/generic/784


Purpose: Log replay test for conflict between a moved directory and a new file created at the old path, followed by file rename and fsync.


Important APIs, helpers, and commands: Defines `list_fs_contents`; uses dmflakey, xfs_io fsync, `_scratch_sync`, and recursive filtered listing.
 Local helper functions detected in the file include `_cleanup`, `list_fs_contents`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`.
 Regression annotations include `_fixed_by_fs_commit btrfs 266273eaf4d9 \`.



Control flow, state, dependencies, risks, and test signals: It creates two dirs, syncs, moves dir1 into dir2, creates a file at the old dir1 path and fsyncs it, moves that file to dir2/foo, fsyncs again, records contents, crashes/remounts, and compares contents by output. State is conflicting inode/name history and log replay metadata. Dependencies are metadata journaling and flakey. Risks are path conflict replay bugs and output normalization. Signals are before/after filesystem listings. Source size is 76 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
