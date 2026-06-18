# sources/test-tools/syzkaller/dashboard/app/tree.go

Purpose: determines a bug's origin/spread across configured kernel repository graphs, labels bugs with origin and missing-backport labels, creates cross-tree patch-test and fix-bisection jobs, and exposes tree-test job details.

Important APIs and types: `generateTreeOriginJobs`, `treeOriginJobDone`, `pollTreeJobResult` variants, `bugTreeContext`, `pollBugTreeJobs`, `setOriginLabels`, `selectRepoLabels`, `labelsCanBeSet`, `missingBackports`, `runRepro`/`doRunRepro`, `Bug.findResult`, `Bug.matchingTreeTests`, `loadCrashInfo`, `isCrashRelevant`, `BugTreeTest.applyPending`, `treeTestJobs`, `crossTreeBisection`, `lazyJobList.lastMatch`, `doneCrossTreeBisection`, `repoGraph`, `repoNode`, and reachability helpers.

Control flow: `generateTreeOriginJobs` runs in a datastore transaction, loads a bug, builds a context, polls tree jobs with manager capabilities, records `NextPoll`/`NeedPoll`, and returns one newly created job if any. `treeOriginJobDone` re-polls after a job finishes with `noNewJobs` so state is updated without spawning recursively. `pollBugTreeJobs` picks a relevant repro crash, clears stale tree tests when crash ID changes, applies pending job results, then combines origin-label and missing-backport workflows.

State and persistence: bug `TreeTests.List` stores per-repo test records with crash ID, repo/branch, optional merge base, pending job key, first/last/firstOK/firstCrash/error job keys. `Bug` labels are mutated for origin and missing-backport results. `Job` entities are created for patch tests and cross-tree fix bisections. Successful cross-tree bisection can set `Bug.FixCandidateJob`.

Dependencies and integration points: App Engine datastore/logging, dashboard job helpers (`addTestJob`, `fetchJob`, `saveJob`, `queryBugJobs`), crash/build helpers, active manager mapping, namespace `KernelRepo` config, `dashapi.ManagerJobs`, and full-bug info job rendering.

Key algorithms: repo graph construction maps aliases, adds inbound/outbound edges from `CommitInflow`, and rejects cycles. Reachability prioritizes merge-only paths before non-merge paths and annotates whether a reachable node is connected only through merge edges. Origin labels are selected by running repros on reachable source and destination trees, then pruning trees whose upstream/downstream neighbors also crash. Missing-backport detection looks for a prior crashing result and a later OK result on inflow trees, then verifies the current repo still crashes before labeling.

Risks: behavior depends on accurate repository aliases, branches, merge semantics, and manager `TestPatches`/`BisectFix` capabilities. Stale manager builds or changed repos make old results misleading, so `isCrashRelevant` rejects deprecated managers and changed manager trees. Retry periods for failed and fixed tree tests are hard-coded. Cross-tree bisection assumes callers do not concurrently create the same job for a manager set.

Test signals: `tree_test.go` covers downstream/lts/upstream origin labels, merge-base testing, repo changes, missing backports, bisection candidate emails, backports pages, commit polling, append config propagation, and repo graph reachability.
