# sources/test-tools/syzkaller/pkg/bisect/bisect.go

## Purpose
Implements syzkaller kernel commit/config bisection for crash causes and fixes, including build/test orchestration, flakiness handling, release-range selection, config minimization, and result confidence.

## Important APIs, Types, and Functions
Public structs are `Config`, `KernelConfig`, `SyzkallerConfig`, `ReproConfig`, and `Result`; public entry point is `Run`. The internal `env` owns repo, bisecter, minimizer, instance environment, current commits, kernel config, timing, report types, reproducibility estimates, cached results, and build config. Major methods include `bisect`, `identifyRewrittenCommit`, `minimizeConfig`, `commitRange*`, `validateCommitRange`, `build`, `test`, `testPredicate`, `revisionHadBug`, `bisectionDecision`, `processResults`, `postTestResult`, `updateFlaky`, `detectNoopChange`, `isTransientError`, and `pickReleaseTags`.

## Control Flow
`Run` validates config, disables coverage, opens repo/env, checks out the branch, and calls `runImpl`. `bisect` prepares the repo, cleans/builds syzkaller, identifies rewritten commits, verifies the crash on the original commit, optionally minimizes config, finds bad/good range for cause or fix bisection, seeds result cache, runs VCS bisection via `testPredicate`, then annotates the result with report, release status, noop-change detection, config, and confidence. `test` builds the kernel for the current revision, runs reproducer trials, classifies results, updates flakiness/confidence, and returns a bisect verdict.

## State and Persistence Behavior
Mutates the kernel checkout by switching commits and building. Uses `instance.Env` to build/test kernels and syzkaller. Saves debug files through the configured tracer, tracks in-memory result cache by commit hash, and returns minimized config bytes. It restores the original HEAD at the end of `runImpl` via defer.

## Dependencies and Integration Points
Depends on `vcs` repository/bisect/config-minimizer interfaces, `instance` build/test environment, `build` error types, manager config, report/crash classification, osutil semaphores, hash signatures, and debug tracing. It is a core backend for syzbot/syz-ci bisection jobs.

## Risks and Test Signals
Risks are high: flaky reproducers, infra errors, build failures on old commits, rewritten branches, cross-tree merge bases, transient crash types, broad config minimization, false negatives, and accidentally deleting confidence through poor report classification. The code contains many safeguards: max trials, skip verdicts, infra aborts, release-tag sampling, recent result cache, transient syz/lost-connection filtering, suspicious deprecation avoidance in other package not here, and noop binary signature detection. The listed subset lacks `bisect_test.go`, so coverage comes from broader package tests and integration bisection runs.
