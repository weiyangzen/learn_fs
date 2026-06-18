# sources/test-tools/xfstests/tests/generic/769


Purpose: Combines reflinked extents with multi-fsblock atomic writes to ensure atomic write restrictions and data integrity survive shared extent layouts.


Important APIs, helpers, and commands: Uses `_require_cp_reflink`, `_require_scratch_reflink`, `_require_scratch_write_atomic_multi_fsblock`, `_weave_reflink_rainbow`, and atomic write helpers.
 It imports `./common/atomicwrites`, `./common/filter`, `./common/preamble`, `./common/reflink`.
 Capability gates include `_require_atomic_write_test_commands`, `_require_block_device`, `_require_cp_reflink`, `_require_scratch`, `_require_scratch_reflink`, `_require_scratch_write_atomic_multi_fsblock`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The test sizes scratch, mounts with reflink support, creates a woven reflink pattern, performs atomic writes across selected ranges, and filters scratch paths. State is shared extent topology and post-write file data. Dependencies are reflink plus atomic write support on the same filesystem. Risks are copy-on-write interactions, insufficient space, and feature combinations that are rare. Signals are helper verification errors or unexpected output. Source size is 88 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
