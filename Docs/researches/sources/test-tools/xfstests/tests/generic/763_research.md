# sources/test-tools/xfstests/tests/generic/763


Purpose: Confirms that a zero-byte write succeeds on a regular file, guarding against exfat returning EFAULT.


Important APIs, helpers, and commands: Uses xfs_io `pwrite 0 0`, `_filter_xfs_io`, and `_require_test`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_test`.
 Regression annotations include `_fixed_by_fs_commit exfat dda0407a2026 \`.



Control flow, state, dependencies, risks, and test signals: The test writes zero bytes to a new file under `$TEST_DIR` and filters the result. State is minimal: the test file may be created but no data should be written. Dependencies are xfs_io and normal write support. Risks are command output differences. Success is normal pwrite output with no error. Source size is 29 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
