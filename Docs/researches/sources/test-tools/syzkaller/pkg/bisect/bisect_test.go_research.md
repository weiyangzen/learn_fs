# sources/test-tools/syzkaller/pkg/bisect/bisect_test.go

Purpose: End-to-end and unit tests for syzkaller kernel bisection logic. The file builds a synthetic git history, injects simulated build/test outcomes, and verifies cause/fix bisection behavior across flaky crashes, broken revisions, equivalent binaries, merge topology, and cross-tree operation.

Important APIs/types/functions: `testEnv` implements the builder/tester surface consumed by `runImpl`, with `BuildKernel`, `CleanKernel`, `BuildSyzkaller`, and `Test`. `createTestRepo` constructs tagged release history and special merge graphs for regression scenarios. `testBisection`, `checkBisectionResult`, `BisectionTest`, `bisectionTests`, `TestBisectionResults`, `TestBisectVerdict`, `TestMostFrequentReport`, and `TestPickReleaseTags` define the core test matrix.

Control flow: `TestBisectionResults` reuses temporary repositories through a channel, validates each `BisectionTest`, creates or reuses the synthetic repo, and runs `testBisection`. `testEnv.Test` determines crash/good/infra/boot results from the current repo HEAD title, baseline config, introduced/fix commit lookup, and optional injected crash types. `testBisection` runs `runImpl` once and usually reruns with a fake hash to verify title-based commit recovery.

State and persistence behavior: Tests persist a real temporary git repository with tags, branches, and merges. The simulated kernel build stores the last config in `testEnv.config` and returns image signatures derived from commit/config hash, with configurable same-binary ranges. There is no production persistence beyond temp dirs.

Dependencies/integration points: Exercises `pkg/vcs`, `pkg/instance`, `pkg/build`, `pkg/mgrconfig`, `pkg/report/crash`, and `debugtracer.TestTracer`. It depends on test OS/arch targets and the production bisection package internals.

Risks: The test relies on commit titles being parseable integers and on git bisection/tag behavior. Parallel tests share repo directories through a cache, so a checkout leak could contaminate later cases. The synthetic environment compresses many real failure modes into deterministic ranges, which is useful but can miss timing, remote build, or flaky infrastructure subtleties.

Test signals: The file itself is the test signal. It covers successful cause/fix bisection, non-repro errors, inconclusive sets, all-release failures, HEAD failures, syz-fatal/lost-connection handling, cross-tree fixes, confidence for flaky repros, verdict thresholds, report preference, and release tag sampling.
