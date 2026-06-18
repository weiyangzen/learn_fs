# sources/test-tools/syzkaller/dashboard/app/aidb/crud.go

## Purpose

`aidb/crud.go` is the Spanner persistence layer for dashboard AI agents, workflows, jobs, trajectories, external report state, review journals, report comments, and patch iteration orchestration. It provides typed CRUD helpers and transactional command handlers used by the dashboard API/UI code.

## Important APIs, types, and functions

- Connection and query helpers: `dbClient`, `CloseClient`, `selectAll`, `selectOne`, `readRow`, `RunInTransaction`, `saveEntity`, `selectAllFrom`, and null conversion helpers.
- Agent/workflow APIs: `LoadActiveWorkflows`, `UpdateWorkflows`, `AgentIsAlive`, and `LoadAgent`.
- Job APIs: `CreateJob`, `StartJob`, `NextStaleJob`, `RestartJob`, `LoadNamespaceJobs`, `LoadBugJobs`, `LoadBugIDsWithPendingPatch`, `LoadJob`, and `SetJobDone`.
- Trajectory APIs: `StoreTrajectorySpan` and `LoadTrajectory`.
- Reporting APIs: `AddJobReportingTransactional`, `LoadPendingJobReportingBySource`, `LoadJobReportings`, `LoadBugJobReportings`, `LoadJobReporting`, `LoadJobReportingByExtID`, and `JobReportingPublished`.
- Command APIs: `UpstreamReportCommand`, `RejectReportCommand`, `UnrejectReportCommand`, `LogCommandError`, and `IsCommandProcessed`.
- Comment/iteration APIs: `SaveJobComment`, `LoadJobComments`, `LoadJobCommentsByReporting`, `LoadPendingCommentGroups`, `CreatePatchIterationJob`, `IterationJobDone`, `hasRunningIterationJob`, `isNewestReport`, `checkBackoff`, `getUnprocessedComments`, and `markCommentsProcessedTx`.
- Structured errors: `ErrNotFound`, `ErrDuplicateComment`, `ErrCannotUpstream`, `ErrCannotReject`, `ErrCannotUnreject`, and `ErrNotAuthorized`.

## Control flow and persistence behavior

The file uses Cloud Spanner read-write transactions where uniqueness, correctness, or multi-row state changes matter. `StartJob` selects the oldest unstarted job matching requested workflows and allowed namespaces, then marks it started in the same transaction. `NextStaleJob` first checks whether the same agent has unfinished work, then checks jobs whose assigned agent is inactive past an eight-hour cutoff; it aborts the original job and inserts a cloned replacement.

External reporting commands are journaled transactionally with job correctness changes and optional `JobReporting` creation. `UpstreamReportCommand` refuses rejected jobs, checks no-parallel conflicts when configured, marks the job correct, writes an approve journal row, and optionally inserts a next-stage reporting row. `RejectReportCommand` marks `Correct=false`; `UnrejectReportCommand` clears correctness. Duplicate command insert conflicts are treated as idempotent no-ops.

Patch iteration creation loads the parent reporting, requires unprocessed comments, rejects already running iteration jobs, drains stale threads when a newer report exists, honors exponential backoff after failed iteration jobs, clones parent args, injects `TargetCommentIDs`, and inserts a `WorkflowPatchIteration` job. `IterationJobDone` marks comments processed, checks staleness again, and inserts a new reporting only when the iteration produced a patch or replies.

## State model

Spanner tables are selected via reflected entity fields: `Agents`, `Workflows`, `Jobs`, `TrajectorySpans`, `Journal`, `JobReporting`, and `JobComments`. JSON data is stored in `spanner.NullJSON` with Spanner configured to decode numbers as `json.Number`. Job lifecycle fields are `Created`, nullable `Started`, nullable `Finished`, `Error`, `Aborted`, `Correct`, `Args`, and `Results`. Reporting lifecycle fields are `CreatedAt`, nullable `ReportedAt`, nullable `UpstreamedAt`, `ExtID`, `Version`, `Stage`, and `Source`. Comments are keyed by generated IDs and carry external IDs, author/body metadata, `Processed`, and DKIM verification.

## Dependencies and integration points

The layer depends on `cloud.google.com/go/spanner`, App Engine app IDs for per-app client caching, `dashapi` request/response types, `pkg/aflow/ai` workflow constants, `pkg/aflow/trajectory`, `pkg/email/lore`, and UUID generation. It is consumed by dashboard AI API handlers, UI handlers, and tests. `dbClient` uses a background context so Spanner clients survive request contexts and are keyed by App Engine app ID.

## Risks and edge cases

Important risks include transaction retries returning stale local variables, which the code explicitly handles by resetting `job` inside transaction closures. Reflection-based `selectAllFrom` can silently change SQL column order when entity structs change, so migrations and tests must stay aligned. `SaveJobComment` maps any Spanner `AlreadyExists` to duplicate comment, but generated IDs make true duplicates unlikely unless schema uniqueness includes external IDs. Patch iteration logic has several race points, so stale-report checks are performed both when creating and finishing iteration jobs. `checkBackoff` relies on completed failed jobs being ordered by `Created`, and version increments depend on parent `Version` being valid when prior reports exist.

## Test signals

The behavior is covered primarily by `ai_test.go` and `ai_report_test.go`: migration idempotency, parallel job polling uniqueness, stale/restarted agents, namespace authorization, external report idempotency, no-parallel reporting, comment processing, patch iteration backoff, and stale-thread draining.
