# sources/test-tools/xfstests/tests/generic/757


Purpose: Uses log-writes plus thin provisioning to replay every FUA point from an async direct-I/O fdatasync workload, targeting Btrfs checksum/log-tree recovery bugs.


Important APIs, helpers, and commands: Imports `dmthin` and `dmlogwrites`; uses fio `libaio` direct random writes with `fdatasync=1`, `_log_writes_*`, `_dmthin_*`, and `_soak_loop_running`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmlogwrites`, `./common/dmthin`, `./common/preamble`.
 Capability gates include `_require_aiodio`, `_require_dm_target`, `_require_fio`, `_require_log_writes`, `_require_scratch_nocheck`.
 Regression annotations include `_fixed_by_fs_commit btrfs e917ff56c8e7 \`.



Control flow, state, dependencies, risks, and test signals: The test configures a thin device under log-writes, mkfs/mounts it, runs fio against a 1GiB file, removes log-writes, finds FUA entries after mkfs, replays ranges to the thin volume, mounts/checks as needed, and advances through FUA points. State includes the log-writes journal, thin volume, replay cursor, and filesystem recovery state. Dependencies are dm-thin, log-writes, fio async DIO, and filesystem check helpers. Risks are replay slowness, missing FUA markers, and XFS dirty-log handling. Success is all replay checkpoints passing filesystem checks. Source size is 94 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
