# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/SnapshotDiffResponse.java

Purpose: Client-facing response wrapper for snapshot diff status and report retrieval.

Important APIs and types: Stores `SnapshotDiffReportOzone`, `JobStatus`, wait time, reason, optional `SubStatus`, progress percentage, and report-only flag. `JobStatus` maps to protobuf job status; `SubStatus` maps to protobuf substatus.

Control flow: Constructors support status with or without reason and report-only semantics. `toString` renders report content for DONE, failure/retry guidance for FAILED/REJECTED/NOT_FOUND, and generic status with optional substatus/progress for active states.

State and persistence behavior: Mutable fields are `subStatus`, `progressPercent`, and `isReportOnly` set through constructors/setters. Persistent job state lives in OM snapshot diff job tables, not this DTO.

Dependencies and integration points: Produced by OM client translator and consumed by CLI/client snapshot diff commands. It wraps `SnapshotDiffReportOzone` and protobuf enum values.

Risks: User-facing strings encode CLI behavior and may be brittle. Progress percentage is appended only for selected substatuses. `snapshotDiffReport` may be null for non-DONE statuses depending on server response assumptions.

Test signals: String rendering for each job status, report-only variants, reason fallback, substatus/progress output, and enum protobuf round-trips.
