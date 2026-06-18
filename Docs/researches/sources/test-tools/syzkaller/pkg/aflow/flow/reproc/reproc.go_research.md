# sources/test-tools/syzkaller/pkg/aflow/flow/reproc/reproc.go

## Purpose

`reproc.go` registers and supports the C reproducer generation workflow. It iteratively researches a bug, generates/probes/compiles/runs standalone C reproducers, asks an oracle agent to classify failures or equivalence, and saves a successful `repro.c`.

## Important APIs, Types, and Functions

Inputs are `ReproCInputs`; outputs are `ai.ReproCOutputs`. Helper actions include `FormatC`, `CompileCProg`, `MergeReproC`, `TruncateLog`, `LoopController`, `ExpandToolkit`, `MergeStrategy`, and `SaveReproC`. Important validators are `validateGeneratorOutputs` and `validateOracleOutputs`. `OracleResult`, `GeneratorResult`, `LoopControllerArgs`, and `LoopControllerResult` carry loop state. Prompt constants define researcher/refiner/generator/oracle behavior.

## Control Flow

The workflow checks out/builds/indexes the kernel, asks an initial researcher for strategy, then enters a `DoWhile` loop controlled by `ContinueSignal`. Each iteration optionally refines strategy from oracle feedback, merges strategy, asks a generator for C code, marks the first candidate as a capability probe until verified, repairs compile errors for up to three inner iterations, runs the C repro with optional strace, truncates logs, asks an oracle to validate probe/repro results, and updates loop state. On success, `LoopController` clears `ContinueSignal`, records the C repro and crash report, and `SaveReproC` writes `repro.c` under the workflow workdir.

## State and Persistence Behavior

Loop state persists in the aflow state map across iterations, especially `CapabilitiesVerified`, `OracleFeedback`, `RawCandidateReproC`, `FormattedReproC`, and `ContinueSignal`. `SaveReproC` writes a real file to `ctx.Workdir/repro.c` only when reproduction succeeds. Kernel/build and VM temp behavior is delegated to underlying actions.

## Dependencies and Integration Points

It depends on kernel actions, crash `RunCRepro`, codesearcher, common tools without git, toolkit expansion, `csource` formatting/building, syzkaller `prog` targets, and aflow control-flow actions. It produces the dashboard-facing `repro-c` workflow.

## Risks and Edge Cases

`FormatCFunc` suppresses formatting errors and returns original code, while `CompileCProg` performs actual compile validation. `extractCCode` returns only the first fenced block. Capability probing is enforced through validation state, but LLM compliance and oracle classification remain important. Terminal environment failures are wrapped as `FlowError`. `SaveReproC` prints to stdout, which can be noisy in service contexts.

## Test Signals

Unit tests cover formatting, log truncation, loop controller success/collision/probe/terminal cases, C code extraction, and oracle validation rules. Full VM reproduction requires integration tests.
