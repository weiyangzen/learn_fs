# sources/test-tools/xfstests/tests/generic/782


Purpose: Btrfs-oriented log replay test ensuring fsync of root directory persists a newly created directory after linking an fsynced file into it.


Important APIs, helpers, and commands: Uses `dmflakey`, xfs_io `pwrite`/`fsync`, `_hexdump`, `_scratch_sync`, and `_flakey_drop_and_remount`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmflakey`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`.
 Regression annotations include `_fixed_by_fs_commit btrfs bfe3d755ef7c \`.



Control flow, state, dependencies, risks, and test signals: It creates and syncs a file, creates a directory, writes/fsyncs the file, hardlinks it into the new directory, fsyncs root, simulates power failure, and verifies root content and file data. State is directory entries, hardlink metadata, file data, and log replay state. Dependencies are journaling and flakey target. Risks are crash simulation and filesystem-specific lost+found filtering. Signals are root listing and hexdump after replay. Source size is 73 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
