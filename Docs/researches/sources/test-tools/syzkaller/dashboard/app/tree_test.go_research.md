# sources/test-tools/syzkaller/dashboard/app/tree_test.go

Purpose: integration and unit tests for cross-tree bug presence analysis, missing-backport detection, cross-tree fix bisection, repo graph reachability, and test harness behavior for tree-origin jobs.

Important tests and fixtures: `TestTreeOriginDownstream`, `TestTreeOriginDownstreamEmail`, `TestTreeOriginBetterReport`, `TestTreeOriginLts`, `TestTreeOriginLtsBisection`, `TestNonfinalFixCandidateBisect`, `TestTreeBisectionBeforeOrigin`, `TestTreeOriginErrors`, `TestOriginTreeNoMerge*`, `TestTreeOriginRepoChanged`, `TestOriginNoNext*`, `TestMissing*Backport`, `TestTreeConfigAppend`, `TestRepoGraph`, and `TestRepoGraphMergeFirst`. Fixture types include `treeTestCtx`, `treeTestEntry`, `treeTestResult`, and `treeTestEntryPeriod`.

Control flow: tests configure namespace `KernelRepo` graphs, upload builds/crashes with repros, define synthetic per-repo job outcomes by day, advance time through `moveToDay`, poll and complete patch-test jobs, then assert bug labels, emails, full-bug tree job lists, bisection job requests, backports page visibility, commit polling, and follow-up emails after commit upload. `treeTestCtx.doJob` maps `JobPollResp` repo/merge-base fields to expected fixture entries and returns OK, crash, or error results.

State and persistence: uses datastore bugs/jobs/builds/crashes through the dashboard test harness, email sink for origin and backport messages, bug label state, bisection fix candidate state, and namespace repo config mutations. The tests check that old tree-test records are reused or cleared when the tested crash/repo changes.

Dependencies and integration points: relies on `tree.go`, reporting/email flows, `dashapi.ManagerJobs`, admin/public HTTP access checks for `/tree-tests/backports` and related namespace pages, commit polling/upload APIs, and test helpers from `util_test.go`.

Risks: the tests intentionally model complex time-dependent workflows; small changes to retry windows, label selection, result ordering, email wording, or bisection eligibility can fail many assertions. Fixture matching sorts repo/branch/merge-base fields, so it verifies semantic targets rather than exact field order. Public/admin visibility expectations for backports pages are part of the security contract.

Test signals: passing tests demonstrate that repo graph logic, origin labels, missing-backport labels, cross-tree bisection creation/dedup/retry, fix-candidate display, and notification/commit flows remain coherent.
