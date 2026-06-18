# sources/test-tools/xfstests/tests/generic/777


Purpose: Basic exportfs/open-by-handle test for linked and unlinked files, without the unique mount ID requirements of generic/756.


Important APIs, helpers, and commands: Defines `create_test_files` and `test_file_handles`; uses `_require_open_by_handle`, `_test_cycle_mount`, and the `open_by_handle` helper.
 Local helper functions detected in the file include `create_test_files`, `test_file_handles`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_open_by_handle`, `_require_test`.



Control flow, state, dependencies, risks, and test signals: It creates handle-test files in `$TEST_DIR`, runs decode checks, cycles the test mount, and exercises stale/non-stale handle behavior across deletion/linking scenarios. State is generated handles and test files. Dependencies are open_by_handle support and exportable filesystem behavior. Risks are privilege requirements and filesystem handle instability. Signals are helper output and stale-handle failures. Source size is 70 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
