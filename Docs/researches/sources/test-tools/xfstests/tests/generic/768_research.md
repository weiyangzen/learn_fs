# sources/test-tools/xfstests/tests/generic/768


Purpose: Exercises multi-filesystem-block atomic writes on a normal scratch block device.


Important APIs, helpers, and commands: Uses `_require_scratch_write_atomic_multi_fsblock`, `_simple_atomic_write`, `_test_atomic_file_writes`, xfs_io, and atomic write unit helpers.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_atomic_write_test_commands`, `_require_block_device`, `_require_scratch`, `_require_scratch_write_atomic_multi_fsblock`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: It formats and mounts scratch, discovers atomic write unit min/max, runs simple atomic writes at boundary sizes, then invokes the common atomic write file tests. State is the scratch file data and atomic write capability metadata. Dependencies are block-device scratch with multi-fsblock atomic writes. Risks are device capability drift and filesystem block-size interactions. Success is silent helper completion. Source size is 68 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
