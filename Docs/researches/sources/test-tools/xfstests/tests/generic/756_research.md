# sources/test-tools/xfstests/tests/generic/756


Purpose: Checks exportfs file handles for linked and unlinked files while verifying unique 64-bit mount IDs through statx/open_by_handle.


Important APIs, helpers, and commands: Defines `create_test_files` and `test_file_handles`; requires `open_by_handle`, exportfs, `STATX_MNT_ID_UNIQUE`, and `AT_HANDLE_MNT_ID_UNIQUE` support.
 Local helper functions detected in the file include `create_test_files`, `test_file_handles`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_exportfs`, `_require_open_by_handle_unique_mountid`, `_require_statx_unique_mountid`, `_require_test`, `_require_test_program`.



Control flow, state, dependencies, risks, and test signals: The script creates 1024 handle-test files, runs the helper with stale-after-delete mode, then with normal linked files, then with hardlink/original-delete and unlink modes. State is generated file handles, hardlink topology, mount IDs, and the test directory. Dependencies are the xfstests `open_by_handle` helper and filesystem export support. Risks are privilege requirements and filesystems with unstable handles. Signals are helper output filtered through `_filter_test_dir` and any stale/non-stale mismatch. Source size is 65 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
