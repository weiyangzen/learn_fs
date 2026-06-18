# sources/test-tools/xfstests/tests/generic/775


Purpose: Checks atomic-write crash consistency across mixed mappings by issuing atomic writes with sync modes, forcing shutdown/remount, and verifying no torn data.


Important APIs, helpers, and commands: Defines `prep_mixed_mapping`, `verify_atomic_write`, `check_data_integrity`, and `mixed_mapping_test`; uses `_require_scratch_shutdown`, atomic write commands, and hexdump verification.
 Local helper functions detected in the file include `check_data_integrity`, `mixed_mapping_test`, `prep_mixed_mapping`, `verify_atomic_write`.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_atomic_write_test_commands`, `_require_scratch_shutdown`, `_require_scratch_write_atomic_multi_fsblock`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: It prepares files with written, unwritten, hole, and mixed mappings, performs atomic writes with different sync flags, cycles through filesystem shutdown/remount, and validates that old or new complete data appears but not mixed torn bytes. State is file extent layout, expected data pattern, and shutdown journal state. Dependencies are atomic writes, scratch shutdown support, and xfs_io. Risks are destructive shutdown and exact data-pattern assumptions. Signals are hexdump/data integrity failures. Source size is 139 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
