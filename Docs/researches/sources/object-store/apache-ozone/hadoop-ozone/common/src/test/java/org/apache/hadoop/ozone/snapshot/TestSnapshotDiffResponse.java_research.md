# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/snapshot/TestSnapshotDiffResponse.java

Purpose: tests user-facing `SnapshotDiffResponse.toString()` messages for report-only snapshot diff polling.

Important APIs/types/functions: exercises `SnapshotDiffResponse` constructors, `toString`, `setSubStatus`, `setProgressPercent`, `SnapshotDiffReportOzone`, `JobStatus`, and `SubStatus`.

Control flow and state: creates an empty snapshot diff report and wraps it in responses with `NOT_FOUND`, `REJECTED`, `FAILED`, and `IN_PROGRESS` statuses in report-only mode. Tests assert strings include guidance for `--get-report`, resubmission guidance, failure reason, sub-status, and progress percentage.

Dependencies and integration points: integrates with snapshot diff CLI/API presentation, `SnapshotDiffReportOzone`, and snapshot diff status enums.

Risks and test signals: catches regressions in operator guidance and status detail visibility. This is not persistence code, but message clarity is important for snapshot diff workflows and automation.
