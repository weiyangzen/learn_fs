# sources/test-tools/xfstests/tests/generic/781


Purpose: Smoke-tests zoned block device support by creating a zloop device inside scratch and running fsx on a filesystem built on that zloop device.


Important APIs, helpers, and commands: Imports `common/zoned`; uses `_create_zloop`, `_destroy_zloop`, `_try_mkfs_dev`, `_mount`, `_unmount`, and `FSX_PROG`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/preamble`, `./common/zoned`.
 Capability gates include `_require_block_device`, `_require_scratch_size`, `_require_zloop`.



Control flow, state, dependencies, risks, and test signals: The script creates and mounts scratch, creates zloop backing storage under scratch, mkfs/mounts the zoned device, runs fsx, and cleans up mounts/devices. State is nested filesystem content and zloop device. Dependencies are zloop support, scratch block device, and fsx. Risks are nested mount cleanup and zloop availability. Success is fsx completion and `Silence is golden`. Source size is 44 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
