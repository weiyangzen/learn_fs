# sources/test-tools/syzkaller/tools/syz-testbed/checkout.go

## Purpose
This file models a checked-out syzkaller variant in `syz-testbed`, tracks its running/completed instances, lazily creates its crash reporter, and performs initial repository checkout/build.

## Important APIs, types, and functions
- `Checkout` holds path/name, manager config JSON, running instance map, completed results, last run timestamp, cached reporter, and mutex.
- `GetReporter` parses partial manager config and lazily constructs `report.Reporter`.
- `AddRunning`, `ArchiveInstance`, `GetRunningResults`, and `GetCompletedResults` synchronize access to instance/result state.
- `TestbedContext.NewCheckout` creates a checkout directory, polls a syzkaller repo/branch, and builds binaries with `syz_instance.MakeBin`.

## Control flow
New checkout creation refuses to reuse an existing path, checks out the configured repo/branch via `vcs.NewSyzkallerRepo(...).Poll`, then runs the syzkaller build with a one-hour timeout. Instance lifecycle methods update `Running` and `Completed` under lock; archiving fetches the instance result before removing it from `Running`.

## State and persistence behavior
Persistent side effects include creating `workdir/checkouts/<name>`, cloning/updating source, and building binaries. Runtime state is held in memory and guarded by `Checkout.mu`. Completed results are not restored from disk on restart.

## Dependencies and integration points
Uses `pkg/vcs`, `pkg/instance.MakeBin`, `pkg/mgrconfig`, `pkg/report`, `pkg/osutil`, and local `Instance`/`RunResult` abstractions. `SyzReproInput.QueryTitle` depends on `GetReporter`.

## Risks and edge cases
Existing checkout paths are fatal to a new testbed run, so restart/resume is not supported. `GetRunningResults` ignores fetch errors, which avoids transient failures but can hide broken instances in live stats. Lazy reporter creation calls `tool.Failf`, terminating the process from a getter on config/report errors.

## Test signals
No direct tests. Tests should cover state transitions, result cloning, existing path refusal, build failure propagation, and reporter caching.
