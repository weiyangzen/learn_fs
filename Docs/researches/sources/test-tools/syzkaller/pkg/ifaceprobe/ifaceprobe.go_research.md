# sources/test-tools/syzkaller/pkg/ifaceprobe/ifaceprobe.go

## Purpose
`ifaceprobe.go` implements the dynamic phase of automatic kernel interface extraction. It discovers filesystem interface paths under `/dev`, `/sys`, `/proc`, `/selinux`, and the executor working directory, probes operations on those files, collects coverage, and maps PCs back to kernel source locations.

## Important APIs, Types, And Functions
`Info` is the top-level result with `Files []FileInfo` and `PCs []PCInfo`. `FileInfo` stores a file name and indexes into the shared PC table. `PCInfo` stores function and source-file names. `Run(ctx, cfg, features, exec)` creates a `prober` and runs it. Key methods are `run`, `submitGlob`, `onGlobDone`, `submitFile`, `constVal`, `noteError`, plus helpers `globList` and `extractFileFilter`.

## Control Flow
`Run` initializes a prober with work channels and delegates to `run`. `run` creates a symbolizer, submits all generated glob requests, starts a goroutine to close `done` after the wait group drains, then consumes completed file descriptors. For each file it combines coverage from the first two calls in every result, deduplicates PCs per file, symbolizes unseen PCs against the configured kernel object, appends non-inline frame metadata to `Info.PCs`, records PC indexes in the file, sorts coverage and files, and finally returns any asynchronously noted error. `submitGlob` sends an important executor glob request. `onGlobDone` logs expansion count, reports glob failures, filters discovered paths, and submits per-file probes. `submitFile` builds six small syzkaller programs around `openat` plus read, write, ioctl, and mmap variants, submits them, waits for each result in a goroutine, records successful results, and sends the descriptor to `done`.

## State And Persistence Behavior
All state is runtime-only: outstanding queue requests, wait-group counts, a buffered `done` channel, a single-error channel, local PC de-dup maps, and the returned `Info`. It does not persist results itself. It depends on executor-side kernel state and coverage collection; probing may interact with real device/sysfs/proc files in a sandbox-disabled environment.

## Dependencies And Integration Points
The package integrates tightly with syzkaller manager config, target constants, program deserialization, executor queue requests/results, feature flags, coverage collection, symbolization, and logging. It uses `csource.FeaturesToFlags`, `flatrpc` request and execution flags, `queue.Executor`, `symbolizer.Make`, and `prog.StrictUnsafe`.

## Risks And Edge Cases
`submitFile` assumes every successful result has at least two calls in `res.Info.Calls`; malformed executor results could panic. Probing runs with `ExecEnvSandboxNone`, so the target environment must be controlled. `extractFileFilter` panics on paths outside expected roots. Glob generation is intentionally broad and can create many requests; filters reduce but do not eliminate scale risk. Only the last non-inline frame is recorded, which may hide inline context. `noteError` records only the first error, while work continues.

## Test Signals
This file has no direct tests in the provided set. High-value tests would fake `queue.Executor` for glob and probe result ordering, verify filtering for `/proc` and `/sys` scale controls, validate PC de-duplication and sorting, and cover error propagation from glob, program execution, and symbolization.
