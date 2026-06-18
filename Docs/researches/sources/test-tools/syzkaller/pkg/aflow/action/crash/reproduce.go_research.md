# sources/test-tools/syzkaller/pkg/aflow/action/crash/reproduce.go

## Purpose

`reproduce.go` implements the crash reproduction action and the lower-level VM test runner. It boots configured kernels, runs syz or C reproducers, aggregates crashes across repeated runs, optionally collects coverage, caches expensive executions, and reports whether the expected crash reproduced.

## Important APIs, Types, and Functions

The exported action is `Reproduce = aflow.NewFuncAction("crash-reproducer", ReproduceFunc)`. `ReproduceArgs` carries manager/VM/kernel/reproducer/strace configuration. `RunTestResult` returns the primary `report.Report`, other reports, boot error, fault injection details, coverage, and raw console output. `RunTest` builds a `mgrconfig.Config`, creates an `instance.Env`, collects runs, and calls `aggregateTestResults`. `ReproduceFuncWithCoverage` caches results in a `cachedExecution` object and returns both the typed action result and cache ID. `LoadCoverage` retrieves cached coverage. `symbolize` maps raw PCs to `symbolizer.Frame`s.

## Control Flow

`RunTest` validates VM type and coverage prerequisites, parses the VM JSON, adjusts QEMU or GCE-specific kernel/image paths, completes a syzkaller manager config, creates an environment and crash reporter, and calls `instance.CollectRuns` for up to six runs looking for three valid runs. Aggregation groups `instance.CrashError`s by title, chooses the most frequent title with lexical tie-breaking, records remaining crash types as secondary reports, records the first boot/test error, and symbolizes coverage only when no crash or boot error occurred. `ReproduceFuncWithCoverage` hashes kernel config, image data, VM config, repros, options, and coverage mode into a cache description. It runs `RunTest` only on a cache miss, converts reports to strings, and converts "no crash" into `aflow.FlowError(ErrDidNotCrash)`.

## State and Persistence Behavior

The action uses aflow's on-disk cache for expensive VM executions and temp directories for per-run work. Cache object IDs are later used by coverage-loading tools. The cache key includes image content hash and repro/option hashes, so VM runs are reused only for equivalent inputs. `Context.Close` releases cached dirs after flow execution.

## Dependencies and Integration Points

It integrates aflow with syzkaller `build`, `instance`, `mgrconfig`, `report`, `symbolizer`, and target metadata. It is used by repro, patching, patch-iteration, and C-repro workflows. GCE support uses `build.EmbedLinuxKernel`; QEMU uses the kernel image path directly. Fault injection extraction comes from the crash reporter.

## Risks and Edge Cases

VM type support is limited to `qemu` and `gce`. Coverage requires a syz repro and is skipped on crashes. Aggregating by report title can conflate or split related crashes depending on title stability. The cache key reads the full image file, which can be expensive. Boot/test errors are returned as normal cached data and later surfaced as errors. `errors.AsType` use for `CrashError` means only correctly wrapped instance errors are recognized. `RunTest` mutates `args.Image` for GCE locally.

## Test Signals

The unit test for `aggregateTestResults` covers single crashes, repeated same-title crashes, flaky runs, majority crash selection, boot errors, and all-ok runs. Full VM behavior requires integration tests or workflow runs with real kernels/images.
