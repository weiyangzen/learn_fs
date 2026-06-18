# sources/test-tools/syzkaller/dashboard/app/jobs_test.go

Purpose: primary integration suite for job lifecycle behavior across email, external APIs, syz-ci polling/completion, bisection, retesting, reset, and reporting.

Important APIs/types/functions: `TestJob`, `TestBootErrorPatch`, `TestTestErrorPatch`, `TestJobWithoutPatch`, `TestReproRetestJob`, `TestDelegatedManagerReproRetest`, `TestJobRestrictedManager`, `TestBisectFixJob`, `TestBisectFixRetry`, `TestNotReportingAlreadyFixed`, `TestFixBisectionsListed`, `TestFixBisectionsDisabled`, `TestExternalPatchFlow`, `TestExternalPatchTestError`, `TestExternalPatchCompletion`, `TestParallelJobs`, `TestJobCauseRetry`, `TestEmailTestCommandNoArgs`, and `TestAliasPatchTestingJob`.

Control flow: tests create bugs/builds/crashes, submit patch jobs through email or API, poll jobs, complete them with success/error/crash/bisection payloads, advance mocked time for retry windows, and inspect emails, reports, and persisted state.

State/persistence: verifies job `IsRunning`, attempts, completion, non-reissue, reset behavior, `HeadReproLevel` changes, bisection state, report suppression, and text blob links.

Dependencies/integration: spans email command handling, reporting stages, build upload, job APIs, manager config/decommissioning, datastore, and fake email sink.

Risks/test signals: exact email body assertions are brittle but protect user-visible contracts; time-dependent tests guard retry freezes and delayed fix bisections.
