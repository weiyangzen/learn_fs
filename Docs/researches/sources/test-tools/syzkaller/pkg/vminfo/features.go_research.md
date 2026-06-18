# sources/test-tools/syzkaller/pkg/vminfo/features.go

## Purpose

`features.go` checks executor/VM support for syzkaller runtime features such as coverage, comparisons, sandboxes, net injection, USB/VHCI/Wi-Fi emulation, and memory dump.

## Important APIs, Types, And Functions

`Feature` stores enabled state, setup requirement, and reason. `Features.Enabled` and `NeedSetup` build bitmasks. `startFeaturesCheck` launches one goroutine per feature and submits a simple program with feature-specific flags. `finishFeatures` merges executor setup info with program-run results and enforces required coverage/memory-dump options. `featureToFlags` maps feature IDs to `ExecEnv`/`ExecFlag`. `featureSucceeded` validates execution and coverage/comparison output.

## Control Flow, State, Dependencies, And Integration

Feature checks run concurrently through `queue.Executor` and communicate over `ctx.features`. Disabled-by-user features still produce reasons. The code sanitizes executor output and requires `FeatureSandboxNone` to work at minimum. It integrates with `Checker.Run` and flatrpc feature descriptors.

## Risks And Test Signals

The `go func()` closure uses `feat` from a range over feature names; in current Go semantics this is safe, but older semantics would capture incorrectly. Unknown features panic. Runtime behavior depends on executor fidelity and feature setup reporting. `vminfo_test.go` exercises all features via synthetic successful queue results.
