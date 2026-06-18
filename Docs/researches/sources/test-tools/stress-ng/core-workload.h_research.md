# sources/test-tools/stress-ng/core-workload.h

## Purpose
`core-workload.h` defines workload method IDs, the method-name mapping type, and the public workload execution API.

## Important APIs, Types, And Functions
It defines IDs for `all`, `fma`, `getpid`, `inc64`, `memmove`, `memread`, `memset`, `mwc64`, `nop`, `pause`, `procname`, `random`, `strnum`, `sqrt`, `time`, `vecfp`, and `vecint`. `stress_workload_method_t` maps names to IDs. Exports are `workload_methods`, `stress_workload_method`, and `stress_workload_waste_time`.

## Control Flow
Option parsing can enumerate `workload_methods` or call `stress_workload_method`; runtime code calls `stress_workload_waste_time` with a method, duration, and scratch buffer.

## State And Persistence
No state is defined in the header. Implementation state includes small static counters and process-name changes for selected methods.

## Dependencies And Integration Points
It relies on common types such as `size_t` and `uint8_t`. The workload stressor and scheduler/load simulation code integrate with the method IDs.

## Risks
The `STRESS_WORKLOAD_METHOD_MAX` macro points to `VECFP` while `VECINT` has the next ID. Any code using max for enumeration or random selection may omit the last method unless it intentionally wants that behavior.

## Test Signals
Build coverage checks the declarations. Runtime `--workload` option tests and method enumeration validate name-to-ID consistency.
