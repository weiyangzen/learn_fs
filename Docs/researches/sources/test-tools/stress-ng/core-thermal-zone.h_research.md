# sources/test-tools/stress-ng/core-thermal-zone.h

## Purpose
`core-thermal-zone.h` defines the thermal-zone data structures and API used for sampling and reporting per-stressor temperature data.

## Important APIs, Types, And Functions
It defines `STRESS_THERMAL_ZONES`, `STRESS_THERMAL_ZONES_MAX`, `stress_tz_info_t`, `stress_tz_stat_t`, and `stress_tz_t`. Exports include `stress_tz_init`, `stress_tz_free`, `stress_tz_temperatures_get`, and `stress_tz_dump`.

## Control Flow
Callers initialize a linked list of zones, collect temperatures into fixed-size per-stressor arrays during execution, dump aggregated results at reporting time, then free the list.

## State And Persistence
The structures hold heap-owned path/type strings, zone ordering metadata, and millidegree-Celsius samples. This is process/shared-memory reporting state only; sysfs is read but not modified.

## Dependencies And Integration Points
It depends on `FILE`, `stress_list_item_t`, and common stress-ng types from the broader include stack. It integrates with `core-vmstat.c`, shared runtime state, YAML reports, and thermal-stat command-line options.

## Risks
The fixed-size `tz_stat` array requires every index to remain below `STRESS_THERMAL_ZONES_MAX`. Consumers must free strings and list nodes exactly once. The unconditional `STRESS_THERMAL_ZONES` definition means non-Linux builds must rely on implementation guards rather than header-level exclusion.

## Test Signals
Compilation validates structure availability. Runtime coverage comes from `--tz`, `--thermalstat`, YAML metric dumps, and machines with multiple duplicated thermal-zone type names.
