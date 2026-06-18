# sources/test-tools/xfstests/tests/generic/771


Purpose: Crash-consistency regression around flakey remount after operations captured by xfs_io output, targeting metadata journaling behavior.


Important APIs, helpers, and commands: Uses `common/dmflakey`, `_init_flakey`, `_flakey_drop_and_remount`, `_filter_xfs_io`, and metadata journaling requirements.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`, `_require_test_program`.
 Regression annotations include `_fixed_by_fs_commit btrfs 0a32e4f0025a \`.



Control flow, state, dependencies, risks, and test signals: The script formats scratch, sets up flakey, performs file operations that are then crash-tested via drop/remount, and validates expected post-replay state through filtered xfs_io output. State lives in the journal/log and scratch files. Dependencies are flakey device-mapper target, scratch, and helper programs. Risks are crash timing and filesystem-specific replay semantics. Signals are filtered mismatches or remount/check failure. Source size is 60 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
