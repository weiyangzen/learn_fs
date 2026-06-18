# sources/storage-engines/foundationdb/contrib/grv_proxy_model/grv_test.py

## Purpose
CLI driver for simulating GRV proxy behavior under selected workload, ratekeeper, proxy model, and limiter implementations.

## Important APIs, Types, And Functions
Imports model registries from `workload_model` and `ratekeeper_model`, proxy/limiter classes from `proxy_model`, `Priority`, and `Plotter`. `print_choices_list()` lists valid workloads, ratekeeper models, proxy classes, and limiters. `validate_class_type()` verifies named classes against required superclasses.

## Control Flow
The script parses workload, ratekeeper, duration, limiter, proxy, list, and graph flags. It currently requires workload and ratekeeper before honoring `--list`. It validates selected names, constructs the limiter and proxy model, runs the simulation, prints latency percentiles and rates per workload priority, and optionally displays plots.

## State And Persistence
State is in the instantiated proxy model and its `results` object. No files are written by this script unless the plotting layer does so externally.

## Dependencies And Integration
Depends on sibling GRV proxy model modules and plotting support. It is a simulation/developer analysis entry point rather than production code.

## Risks
Because workload/ratekeeper validation happens before `--list`, `--list` alone exits with an error after printing choices instead of serving as a pure list command. Percentile indexing uses `int(p * len(latencies))`, which can equal `len` only for 1.0 not used here, but small samples can duplicate indexes. Imported `Priority` is unused. Plot display can block in headless environments unless `--no-graph` is used.

## Test Signals
Run `--list`, invalid model names, valid simulation with `--no-graph`, short duration, empty latency output, and each limiter naming style with and without `Limiter` suffix.
