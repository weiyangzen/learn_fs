# sources/test-tools/xfstests/tests/generic/779


Purpose: Crash-consistency test for symlink inode-copy logging across dm-flakey power failure.


Important APIs, helpers, and commands: Uses `dmflakey`, `_require_symlinks`, `_flakey_drop_and_remount`, `_INODE_COPY_EVERYTHING`-related regression annotation, and scratch journaling.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`, `_require_symlinks`.
 Regression annotations include `_fixed_by_fs_commit btrfs 953902e4fb4c \`.



Control flow, state, dependencies, risks, and test signals: The test creates symlink-related metadata, forces relevant inode changes, drops/remounts through flakey, and verifies expected symlink/directory state. State is symlink inode metadata and filesystem log. Dependencies are symlinks, metadata journaling, and flakey target. Risks are filesystem-specific log replay and limited visible output. Signals are missing/corrupt symlink state or remount failure. Source size is 60 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
