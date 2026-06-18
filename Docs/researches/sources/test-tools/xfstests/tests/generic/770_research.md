# sources/test-tools/xfstests/tests/generic/770


Purpose: Exercises atomic writes across a deliberately fragmented file layout without reflink, stressing allocation boundaries and free-space constraints.


Important APIs, helpers, and commands: Uses `_weave_file_rainbow`, `_get_available_space`, `_require_scratch_write_atomic_multi_fsblock`, and atomic write helpers.
 It imports `./common/atomicwrites`, `./common/filter`, `./common/preamble`, `./common/reflink`.
 Capability gates include `_require_atomic_write_test_commands`, `_require_block_device`, `_require_scratch`, `_require_scratch_write_atomic_multi_fsblock`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The flow mkfs-sizes scratch, computes atomic unit and block size values, builds a woven file extent pattern, then performs atomic writes over those ranges. State is fragmented extent mapping and written data. Dependencies are scratch block device and atomic write support. Risks are available-space calculations, allocator differences, and atomic unit alignment. Test signals are helper data-integrity failures. Source size is 129 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
