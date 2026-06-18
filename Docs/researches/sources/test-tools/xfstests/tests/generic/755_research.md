# sources/test-tools/xfstests/tests/generic/755


Purpose: Verifies that unlinking one hardlink updates the target inode ctime.


Important APIs, helpers, and commands: Uses `_require_hardlinks`, `stat -c %Z`, `ln`, `unlink`, and a two-second sleep to cross timestamp granularity.
 It imports `./common/preamble`.
 Capability gates include `_require_hardlinks`, `_require_test`.
 Regression annotations include `_fixed_by_fs_commit btrfs 3bc2ac2f8f0b \`.



Control flow, state, dependencies, risks, and test signals: The test creates a file and hardlink in `$TEST_DIR`, records ctime, sleeps, unlinks one name, records ctime through the remaining name, and reports if it did not change. State is link count and ctime in the test filesystem. Dependencies are hardlinks and second-resolution timestamp visibility. Risks are coarse or frozen timestamps and clock behavior. Success signal is only `Silence is golden`. Source size is 40 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
