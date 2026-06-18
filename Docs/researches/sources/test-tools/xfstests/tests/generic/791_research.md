# sources/test-tools/xfstests/tests/generic/791


Purpose: Checks fsnotify/fanotify delivery of file I/O errors by injecting a dm-error range into a file extent and reading/writing through buffered and direct I/O.


Important APIs, helpers, and commands: Imports `common/dmerror`, `common/systemd`, and filters; defines `filter_fsnotify_errors`; uses `fs-monitor`, xfs_io `fiemap`, `min_dio_alignment`, `_dmerror_mark_range_bad/good`, and `_require_fanotify_ioerrors`.
 Local helper functions detected in the file include `_cleanup`, `filter_fsnotify_errors`.
 It imports `./common/dmerror`, `./common/filter`, `./common/fuzzy`, `./common/preamble`, `./common/systemd`.
 Capability gates include `_require_dm_target`, `_require_fanotify_ioerrors`, `_require_odirect`, `_require_scratch`, `_require_test_program`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: It formats/mounts scratch, ensures XFS non-zoned when needed, writes a 4-block file, parses its physical extent, aligns a bad sector to device LBA, starts fs-monitor, marks that range bad, runs buffered/direct read and write probes, marks it good, kills monitor and reports errors, then remounts/restarts monitor to confirm errors do not persist. State is dm-error map, fsnotify event stream, victim file extent, and temp monitor logs. Dependencies are fanotify FS error support, dm-error, direct I/O, and fiemap. Risks are extent parsing, LBA alignment, and coalesced event semantics. Signals are normalized FAN_FS_ERROR records only during the bad-device phase. Source size is 213 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
