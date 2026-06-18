# sources/test-tools/xfstests/tests/generic/767


Purpose: Validates atomic write reporting and simple atomic writes on a scsi_debug device wired in as scratch storage.


Important APIs, helpers, and commands: Uses `_require_scsi_debug`, `_get_scsi_debug_dev`, `_put_scsi_debug_dev`, `_require_scratch_write_atomic`, `_simple_atomic_write`, `_test_atomic_file_writes`, and statx atomic fields.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/atomicwrites`, `./common/preamble`, `./common/scsi_debug`.
 Capability gates include `_require_block_device`, `_require_scratch`, `_require_scratch_write_atomic`, `_require_scsi_debug`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The flow provisions a scsi_debug block device with atomic write capability, assigns it to scratch, mkfs/mounts, checks min/opt/max atomic units, performs simple atomic writes at multiple sizes, and tears the device down in cleanup. State is external scratch block device identity and scratch contents. Dependencies are scsi_debug module access, block-device scratch, xfs/ext4 support, and atomic write helpers. Risks include module cleanup leaks and device capability mismatch. Signals are statx/capability mismatches or write verification failures. Source size is 104 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
