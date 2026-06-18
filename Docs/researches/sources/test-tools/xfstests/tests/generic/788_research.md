# sources/test-tools/xfstests/tests/generic/788


Purpose: Verifies that truncate(2) is blocked on fsverity-enabled files.


Important APIs, helpers, and commands: Imports `common/verity`; uses `_disable_fsverity_signatures`, `_scratch_mkfs_verity`, `_fsv_create_enable_file`, `_fsv_scratch_begin_subtest`, and the `truncate` helper.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`, `./common/verity`.
 Capability gates include `_require_scratch_verity`, `_require_test_program`.



Control flow, state, dependencies, risks, and test signals: It disables signature enforcement for the test, creates a verity-capable scratch filesystem, enables fsverity on a file, then invokes the compiled truncate helper expecting failure. State is fsverity metadata and signature policy restored by cleanup. Dependencies are fsverity scratch support and helper binary. Risks are cleanup of signature policy and filesystems without verity. Signal is the helper’s expected failure output under the subtest. Source size is 38 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
