# sources/test-tools/syzkaller/dashboard/app/jobs.go

Purpose: orchestrates syz-ci jobs: patch tests, reproducer retests, cause/fix bisections, tree/cross-tree jobs, polling/reset/completion APIs, result reporting, invalidation, and backport tracking.

Important APIs/types/functions: `testReqArgs`, `testJobArgs`, `handleTestRequest`, `addTestJob`, `saveJob`, `patchTestJobArgs`, `checkTestJob`, `pollPendingJobs`, `getNextJob`, `loadPendingJob`, `createJobResp`, `resetJobs`, `doneJob`, `updateBugBisection`, `pollCompletedJobs`, `createBugReportForJob`, `jobReported`, `handleExternalTestRequest`, `activeManager`, `extJobID`, `jobID2Key`, `makeJobInfo`, `queryBugJobs`, and backport helpers.

Control flow: patch requests validate user/repo/branch/repro/status, store text blobs, deduplicate by `ExtID`, create child `Job` entities, and reference crashes. Polling returns matching pending jobs or throttles automatic generation. `createJobResp` loads patch/crash/build/config/repro data and marks the job running. `doneJob` stores result blobs/build/commits, updates bisection or repro state, saves job/bug, then runs post-job handlers.

State/persistence: jobs are child datastore entities under bugs. State transitions from pending to running to finished to reported; text blobs store patches/logs/errors/reports/configs. Bisections mutate bug bisection fields and sometimes fix-candidate/fix state.

Dependencies/integration: integrates dashapi, email/reporting, datastore, manager config, build/crash/text storage, tree-origin/cross-tree code, VCS validation, and UI job info.

Risks/test signals: high concurrency around polling, reset, duplicate email delivery, and completion; datastore group limits force some reads outside transactions; generated-job throttling mutates the managers map; bisection result reporting is intentionally selective. `jobs_test.go` provides broad integration coverage.
