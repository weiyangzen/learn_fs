# sources/test-tools/stress-ng/core-thermal-zone.c

## Purpose
`core-thermal-zone.c` discovers Linux thermal zones, samples their temperatures, and emits per-stressor thermal summaries in human-readable and YAML output.

## Important APIs, Types, And Functions
`stress_tz_init` scans `/sys/class/thermal/thermal_zone*/type`, normalizes type names, de-duplicates repeated type names with an instance counter, sorts insertion by type, and assigns stable indices. `stress_tz_free` releases the linked list. `stress_tz_temperatures_get` reads `temp` files into a `stress_tz_t` sample. `stress_tz_dump` aggregates recorded temperatures across stressor instances and writes informational/YAML output. Internal helpers include `stress_tz_type_instance`, `stress_tz_type_fix`, `stress_tz_insert`, and `stress_tz_compare`.

## Control Flow
Initialization walks thermal-zone directory entries up to `STRESS_THERMAL_ZONES_MAX`, allocates a node per valid zone, reads and sanitizes the type, inserts the node in lexical order, and then assigns indices. During stressor runs, samples are stored by zone index. At report time, the code copies zone pointers into an array, sorts by type and instance, averages valid temperatures at or below 250 C across non-ignored stressor instances, and prints per-stressor readings.

## State And Persistence
The persistent system data is read-only sysfs state. Runtime state is the linked list in `g_shared->tz_info` and per-stressor `tz_stat` arrays. The module allocates heap memory for paths/types and temporary arrays, all freed by `stress_tz_free` or local cleanup.

## Dependencies And Integration Points
It depends on Linux thermal sysfs layout, `core-sort.h` for `shim_qsort`, `stress_list_item_t` statistics, shared globals, and YAML/log output helpers. `core-vmstat.c` uses the discovered list for periodic `--thermalstat` output.

## Risks
Sysfs may be absent, incomplete, dynamically changing, or expose unexpected names. Any failure to read a type aborts initialization with `-1`, which may disable thermal reporting more broadly than necessary. The fixed maximum of 31 zones bounds memory but can omit zones on large systems.

## Test Signals
Runtime signals come from `--tz`, `--thermalstat`, and kernel coverage runs that enable thermal output. Machines without thermal zones should report unavailable temperatures rather than failing stressor execution.
