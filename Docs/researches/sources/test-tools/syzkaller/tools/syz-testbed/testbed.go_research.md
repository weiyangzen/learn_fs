# sources/test-tools/syzkaller/tools/syz-testbed/testbed.go

## Purpose
`syz-testbed` orchestrates checkout/build/run/collect loops for comparing syzkaller variants or benchmarking repro behavior over time.

## Important APIs, types, and functions
- Config types: `TestbedConfig`, `DurationConfig`, `CheckoutConfig`, `ReproTestConfig`, and runtime `TestbedContext`.
- `main` loads defaults plus JSON config, validates it, starts HTTP/stats goroutines, creates checkouts, and enters the slot loop.
- `MakeMgrConfig` merges base and per-checkout manager config and forces manager HTTP to `:0`.
- `GetStatViews`, `TestbedStatsTable`, and `SaveStats` derive completed/all views and persist stats.
- `Slot` repeatedly creates target jobs, runs instances, stops/archives them, and reports errors.
- `Loop` runs `MaxInstances` slots until interrupt or any slot error.
- `DurationConfig` JSON marshaling and config validation helpers support config parsing.

## Control flow
After config validation, every checkout is cloned and built before slots start. Each slot repeatedly asks the target for a new job, marks it running, runs it in a goroutine, waits for stop or completion, archives normal results, and starts another. The top-level loop closes all slots on interrupt or first error and waits for every slot to report.

## State and persistence behavior
Persistent state lives under the configured workdir: checkouts, run folders, stats CSVs, averaged bench files, and testbed summary CSV. Runtime counters and checkout lists live in memory. Periodic `SaveStats` runs every 90 seconds and is serialized by `ctx.mu`.

## Dependencies and integration points
Uses `pkg/config`, `pkg/osutil`, `pkg/tool`, `pkg/vcs`, target strategies, checkout/instance/stats/table code, and optional `syz-benchcmp` path. HTTP setup is delegated to `html.go`.

## Risks and edge cases
The HTTP goroutine starts even when HTTP config is empty. `Loop` expects every slot to send an error after `stopAll` closes; a slot blocked in job creation or shutdown can hang shutdown. Existing checkout directories prevent restart. `SaveStats` periodically reads live instance outputs, which can race with files being written but uses fetch errors defensively in some paths.

## Test signals
No direct tests. High-value integration tests would use fake targets/instances to cover slot lifecycle, config validation, stats saving, interrupt shutdown, and error propagation.
