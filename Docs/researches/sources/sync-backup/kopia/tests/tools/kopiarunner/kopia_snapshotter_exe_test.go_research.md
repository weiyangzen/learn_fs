<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter_exe_test.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter_exe_test.go

This file integration-tests snapshot listing against a real Kopia executable. It creates a filesystem repo, verifies the initial snapshot list is empty, creates snapshots, and checks both snapshot-list and manifest-list methods return the expected count and include the latest snapshot ID.

The helper `snapIDIsLastInList` checks ordering assumptions. The test is gated by executable availability through runner construction.

Risks covered include CLI output parsing and manifest/snapshot list consistency. Residual risks include server mode, S3 repositories, and different CLI output formats across versions. This is a strong signal for `KopiaSnapshotter.ListSnapshots`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter_exe_test.go -->
