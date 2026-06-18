<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/ycsb.go -->
# sources/storage-engines/pebble/cmd/pebble/ycsb.go

## Purpose
Defines `pebble bench ycsb <dir>`, a configurable YCSB workload runner.

## Important APIs, Types, and Functions
`ycsbConfig` is `bench.DefaultYCSBConfig()`. `ycsbCmd` declares usage and detailed help for workload and distribution flags. `initYCSB` binds batch, key distribution, initial/prepopulated key counts, op limit, scan length, workload mix, and value distribution. `runYcsb` installs a rate limiter and delegates to `bench.RunYCSB`.

## Control Flow
After Cobra parses one directory argument and flags, `runYcsb` constructs the shared rate limiter and passes config to the benchmark package.

## State and Persistence Behavior
The wrapper stores config in globals. The YCSB benchmark populates and mutates a Pebble DB according to workload, key distribution, and shared DB options.

## Dependencies and Integration Points
Depends on `bench.YCSBConfig`, `randvar` flag types, Cobra, shared `commonCfg`, and `random.go` rate limiting. The helper is reused by `tombstone.go`.

## Risks and Edge Cases
The `cfg.Batch`, `cfg.Scans`, and `cfg.Values` fields are type-asserted to specific randvar flag types; incompatible config implementations would panic. Workload strings are validated in the bench package, not here. Global config reuse can leak state between runs.

## Test Signals
No direct tests. Useful signals are parsing standard A-F and custom workload mixes, respecting op limits and initial/prepopulated key counts, and applying rate limiter settings.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/ycsb.go -->
