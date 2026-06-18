<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/write_bench.go -->
# sources/storage-engines/pebble/cmd/pebble/write_bench.go

## Purpose
Defines `pebble bench write <dir>`, a YCSB-F based benchmark that searches for sustainable write throughput.

## Important APIs, Types, and Functions
`writeBenchConfig` is `bench.DefaultWriteBenchConfig()`. `writeBenchCmd` declares CLI help and execution. `initWriteBench` binds workload, rate search, concurrency, L0 target, cooloff/test-period, wipe, and debug flags. `runWriteBenchmark` delegates to `bench.RunWriteBench`.

## Control Flow
The benchmark wrapper parses flags, then `bench.RunWriteBench` repeatedly tests write rates, classifies pass/fail according to L0 and write-stall heuristics, cools off after failures, and computes an optimal sustained rate. The search logic is documented in the command's long help but implemented in `bench`.

## State and Persistence Behavior
This file changes only config state. The benchmark itself writes to the target database, may wipe it first, and tracks rate-classification state in process.

## Dependencies and Integration Points
Depends on Cobra and `bench.WriteBenchConfig`. It shares `commonCfg.Wipe` with other benchmark commands and uses shared duration flags bound in `main.go`.

## Risks and Edge Cases
The command-level text has one extra quote in "fails\""; harmless but visible. Rate search can stress storage heavily; guardrails depend on duration, max-size, and benchmark heuristics. Global config reuse can affect repeated in-process use.

## Test Signals
No direct tests. Signals are flag parsing, convergence behavior, correct pass/fail classification, and final optimal write-load reporting from `bench.RunWriteBench`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/write_bench.go -->
