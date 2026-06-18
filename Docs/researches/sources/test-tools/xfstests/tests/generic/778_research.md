# sources/test-tools/xfstests/tests/generic/778


Purpose: Comprehensive atomic-write torn-write detector that races repeated atomic writes with forced shutdowns across written, unwritten, hole, mixed, and append cases.


Important APIs, helpers, and commands: Defines many helpers including `atomic_write_loop`, `start_atomic_write_and_shutdown`, `test_torn_write*`, `test_append_torn_write`, `populate_expected_data`, and `verify_data_blocks`; uses `_soak_loop_running`, scratch shutdown, xfs_io, and atomic write helpers.
 Local helper functions detected in the file include `_cleanup`, `atomic_write_loop`, `create_mixed_mappings`, `dry_run`, `kill_awloop`, `populate_expected_data`, `start_atomic_write_and_shutdown`, `test_append_torn_write`, `test_torn_write`, `test_torn_write_hole`, `test_torn_write_mixed`, `test_torn_write_unwritten`.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_atomic_write_test_commands`, `_require_scratch_shutdown`, `_require_scratch_write_atomic_multi_fsblock`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: It dry-runs expected layouts, starts background atomic write loops, shuts the filesystem down at controlled points, remounts/cycles, and checks every block against old/new/zero expected data. State includes run/kill files, background writer PID, expected data arrays, and crash-recovered scratch contents. Dependencies are multi-fsblock atomic writes and shutdown support. Risks are timing sensitivity, long runtime, and cleanup of background loops. Signals are explicit torn-write data mismatch reports. Source size is 413 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
