# sources/test-tools/syzkaller/syz-ci/jobs.go

Purpose: dashboard job processor for syz-ci patch testing, bisection, and commit polling.

Important APIs/types/functions: `JobManager`, `JobProcessor`, `newJobManager`, `startLoop`, `loop`, `needParallelProcessor`, `resetJobs`, `pollCommits`, `pollManagerCommits`, `pollRepo`, `getCommitInfo`, `pollJobs`, `processJob`, `Job`, `process`, `bisect`, `ignoreBisectCommit`, `testPatch`, `initJobRepo`, `prepareBisectionRepo`, `checkoutJobCommit`, `checkoutKernelOrCommit`, `aggregateTestResults`, `Logf`, and `Errorf`.

Control flow: job manager resets outstanding dashboard jobs, starts one or two processors, polls commit/job ticks, maps dashboard job requests to managers, prepares isolated job workdirs/repos, validates required fields, then either runs patch testing through `instance.Env` or bisection through `pkg/bisect`. Results are converted to `dashapi.JobDoneReq` and reported unless shutdown made an error unreliable.

State and persistence: uses `jobs/` and optionally `jobs-2/` directories for kernel clones, syzkaller checkout, workdir, and debug traces. Workdir is removed per job; debug traces may persist under `jobs/debug`.

Dependencies and integration points: integrates dashboard job API, kernel VCS, instance VM/build/test APIs, bisection, build/test semaphores, and manager configs.

Risks: long bisections can occupy resources for hours. Git clone/reference logic can fall back to fresh fetch. Job validation is strict but downstream build/test failures are environment-heavy. Patch tests intentionally overcommit only on VM types that allow it.

Test signals: `jobs_test.go` covers aggregate result prioritization; broader behavior relies on dashboard/integration tests.
