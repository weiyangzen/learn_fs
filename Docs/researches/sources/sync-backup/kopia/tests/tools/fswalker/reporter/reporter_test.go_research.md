<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/reporter/reporter_test.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/reporter/reporter_test.go

This file tests the reporter wrapper with walk files. It constructs fswalker protobuf data, writes before/after inputs, invokes `ReportFiles`, and asserts the report detects expected differences.

The test validates temp config generation, textproto writing, reporter loading, walk-file reading, and comparison output. It depends on fswalker protobuf structures and test logging.

Risks not covered include in-memory `Report` path, cleanup failures, and large reports. The test is a targeted signal that the wrapper can interoperate with the upstream fswalker reporter.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/reporter/reporter_test.go -->
