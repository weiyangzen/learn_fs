<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/walker/walker_test.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/walker/walker_test.go

This file tests fswalker walker wrapper behavior. `TestWalk` creates a test directory tree, runs a walk policy, and verifies output contains expected files. `TestWalkFail` checks error behavior for invalid policy/path scenarios.

These tests validate temporary policy generation, upstream walker integration, and captured protobuf output. Dependencies include `testdirtree`, fswalker protobufs, and test logging.

Risks covered include basic walker invocation failures. Residual risks include large-file hash cutoffs, symlink edge cases, and platform-specific filesystem metadata differences. The tests support robustness snapshot comparison reliability.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/walker/walker_test.go -->
