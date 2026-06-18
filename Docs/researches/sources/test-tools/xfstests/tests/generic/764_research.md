# sources/test-tools/xfstests/tests/generic/764


Purpose: Crash-consistency test that fsyncing an unlinked-but-open file persists deletion after simulated power failure.


Important APIs, helpers, and commands: Imports `dmflakey`; uses `_init_flakey`, `_flakey_drop_and_remount`, `multi_open_unlink -F -S`, and `_require_metadata_journaling`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`, `_require_test_program`.
 Regression annotations include `_fixed_by_fs_commit btrfs 5e85262e542d \`.



Control flow, state, dependencies, risks, and test signals: It creates a directory, runs a helper that opens, unlinks, fsyncs, and closes a file with no hardlinks, drops/remounts through dm-flakey, and lists the directory expecting it empty. State is log/journal state for an orphaned inode and the dm-flakey mapping. Dependencies are flakey target, journaling, scratch, and helper binary. Risks are destructive crash simulation and helper semantics. Signal is any remaining directory entry or remount failure. Source size is 50 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
