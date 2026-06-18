# sources/test-tools/syzkaller/dashboard/app/ai_report_test.go

## Purpose

`ai_report_test.go` is an integration-heavy test suite for the dashboard's AI patch reporting lifecycle. It exercises how finished AI patching jobs become external report drafts, how reports are confirmed as published, how reviewer commands approve/reject/unreject patches, and how review comments create patch-iteration jobs. The file targets the newer Spanner-backed AI tables through public dashboard API clients and the existing App Engine test context.

## Important helpers, tests, and APIs

- `(*Ctx).setupAIPatchJob` creates a build, reports a reproducible crash, registers the patching workflow with an agent, and creates a Spanner AI job tied to the resulting bug.
- `(*Ctx).finishAIPatchJob` completes an AI job with default patch results (`PatchDescription`, `PatchDiff`, `KernelRepo`, `KernelCommit`) and optional overrides.
- `TestAIExternalReporting` covers the full moderation-to-public reporting path, including `AIPollReport`, `AIConfirmReport`, `AIReportCommand` upstream/reject/unreject commands, `LoadUIJobReviewHistory`, and `aidb.LoadJob`.
- `TestAINoParallelReports`, `TestAIUpstreamTwice`, `TestAIUpstreamIdempotency`, and `TestAIUpstreamConcurrent` cover exclusivity, stage ordering, idempotency by external message ID, and races between iteration and upstream commands.
- `TestAIPatchIterationSuccess`, `testExtendedPatchIteration`, `TestAIPatchIterationBackoff`, `TestAIPatchIterationReplySuccess`, `TestAIPatchIterationEmptyResult`, and `TestAIManualIteration` validate comment ingestion, debounce, patch history construction, changelog/version propagation, reply-only outputs, backoff, stale-thread handling, and manual iteration.
- `TestAIManualPushToReporting`, `TestAIAssessmentNoReport`, `TestAIPatchFilter`, and `TestAIActionEmailsAuth` validate UI-driven reporting pushes, non-patch assessment behavior, bug-list filtering for pending AI patches, and command authorization/DKIM checks.

## Control flow and state behavior

Most tests set an `AIConfig` on namespace `ains`, then simulate a crash to create a bug and a patching job. Completion through `AIJobDone` writes job results to Spanner. Reporting poll calls then materialize `JobReporting` rows into `dashapi.ReportPollResult` values. Confirmation calls set `ReportedAt` and `ExtID`, and command calls use the external ID to locate the active reporting thread.

Patch iteration tests follow a stricter sequence: publish an initial report, submit external comments with root/message IDs, advance mocked time past the 30-minute debounce, poll an agent for `ai.WorkflowPatchIteration`, then finish that job with either a new patch, replies, or empty output. A new patch creates another `JobReporting` row with incremented patch version; replies create reply-only report payloads; empty results mark comments processed without producing an outgoing report.

The tests intentionally check persistence through `aidb.LoadJob`, `aidb.LoadJobReportings`, `aidb.LoadJobComments`, `aidb.LoadBugIDsWithPendingPatch`, and `aidb.RunInTransaction`. They verify `Job.Correct` transitions among unset, true, and false; `Journal` review history ordering; `JobComment.Processed` transitions; and `JobReporting.Version`, `ReportedAt`, and external message links.

## Dependencies and integration points

The suite integrates `dashboard/dashapi`, `dashboard/app/aidb`, `pkg/aflow/ai`, Cloud Spanner emulator context from `NewSpannerCtx`, App Engine mock context, and dashboard UI handlers reached through `GET`, `POSTForm`, and authenticated variants. It also depends on lore-style external report IDs because `JobReporting.ExternalLink` and report command lookup treat `Source: lore` specially.

## Risks and edge cases

The highest-risk behavior is concurrency and idempotency. The tests guard against duplicate upstream commands, duplicate or out-of-order stage transitions, parallel reports for exclusive stages, stale patch-version threads generating reports, and comments arriving while an iteration job is already running. Authorization risk is covered by checking allowed author lists and DKIM before accepting external commands, with failed command attempts journaled so retries are idempotent. Patch-version risk is covered by validating changelog entries and resetting version when a patch is promoted to the next stage.

## Test signals

This file itself is a strong test signal for AI reporting. It asserts complete response payloads, persisted Spanner fields, UI history, authorization errors, and lack of pending reports in terminal states. It also uses mocked time to make debounce/backoff behavior deterministic and uses repeated calls to prove idempotency.
