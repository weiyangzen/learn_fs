# sources/test-tools/syzkaller/dashboard/app/commit_poll_test.go

Purpose: integration test for dashboard commit polling, which tells managers/builders which fixing commit titles still need commit hashes.

Important test: `TestCommitPoll` uploads a build and two crashes, verifies initial poll returns configured repos and no pending commits, marks one bug with two fix commit titles, and checks both appear repeatedly until matching hashes are uploaded. It then uploads commit metadata with one matching title, one unrelated title associated with the second bug, and unrelated commits, confirming only unresolved titles remain. Finally it uploads the remaining hashes and verifies the pending list becomes empty.

Control flow under test: build/crash upload, global bug polling, `ReportingUpdate` with `FixCommits`, `CommitPoll`, and `UploadCommits`.

State and persistence behavior: tests persisted bug fix-commit titles and uploaded commit metadata. It verifies commit-poll output is derived from unresolved title-to-hash matching rather than simply from bug status or commit upload presence.

Dependencies and integration points: uses `dashapi.BugUpdate`, `dashapi.Commit`, namespace repo configuration from `testConfig`, manager client API methods, and sorting for deterministic assertions.

Risks covered: duplicate polling stability, unrelated commit uploads polluting pending lists, commits attached by bug ID not immediately replacing title-based fix requests unless the requested title is resolved, and repo list correctness. The test does not cover multi-namespace or branch-specific polling edge cases.
