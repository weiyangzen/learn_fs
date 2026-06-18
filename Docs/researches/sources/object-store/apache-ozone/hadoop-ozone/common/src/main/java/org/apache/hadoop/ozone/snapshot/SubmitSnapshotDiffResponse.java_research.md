# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/SubmitSnapshotDiffResponse.java

Purpose: Client-facing response wrapper for submit-snapshot-diff calls.

Important APIs and types: Stores a response string. One constructor formats status-aware guidance from wait time, previous job status, and previous reason; another accepts a server-provided response string.

Control flow: If a previous status exists and is not QUEUED, the formatted constructor mentions it and optional reason. DONE and IN_PROGRESS guide the user to `--get-report`; other statuses state that a new job was submitted and provide retry timing.

State and persistence behavior: In-memory immutable string wrapper. Snapshot diff job state is server-side.

Dependencies and integration points: Returned by the OM client translator for `submitSnapshotDiff` and rendered by CLI code.

Risks: User-facing command guidance is embedded in the DTO and can drift from CLI options. The translator currently uses the raw server response constructor, so the formatting constructor is for server/client compatibility paths.

Test signals: Formatting tests for null/QUEUED/DONE/IN_PROGRESS/FAILED statuses, reason inclusion, wait time rendering, and server response passthrough.
