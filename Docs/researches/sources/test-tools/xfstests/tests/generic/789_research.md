# sources/test-tools/xfstests/tests/generic/789


Purpose: Log replay test that truncating a file to zero, fsyncing it, hardlinking it, and fsyncing the directory persists zero size and link after crash.


Important APIs, helpers, and commands: Uses dmflakey, xfs_io pwrite/truncate/fsync, stat size/link count checks, and `_flakey_drop_and_remount`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`.
 Regression annotations include `_fixed_by_fs_commit btrfs 5254d4181add \`.



Control flow, state, dependencies, risks, and test signals: It writes and syncs a file, truncates/fsyncs it to zero, creates a sibling hardlink, fsyncs the directory, drops/remounts, and prints file size/link count plus missing-link diagnostics. State is file size, nlink, directory entry, and log replay. Dependencies are journaling and flakey target. Risks are crash simulation and filesystem-specific log replay. Signals are size 0, link count 2, and existing `dir/bar`. Source size is 59 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
