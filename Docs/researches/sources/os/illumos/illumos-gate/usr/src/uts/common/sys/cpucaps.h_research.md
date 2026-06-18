# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpucaps.h

## Role

Defines the public kernel CPU caps interface for enforcing hard CPU usage limits at project or zone level.

## Key Constants and State

- `MAXCAP`: maximum cap value; specifying it disables the cap.
- `cpucaps_enabled`: fast global enable check.
- `CPUCAPS_ON()`, `CPUCAPS_OFF()`: guard macros.

## Framework Interfaces

- Initialization:
  - `cpucaps_init()`
- Project/zone lifecycle:
  - `cpucaps_project_add()`
  - `cpucaps_project_remove()`
  - `cpucaps_zone_remove()`
- Cap control:
  - `cpucaps_project_set()`
  - `cpucaps_zone_set()`
  - `cpucaps_project_get()`
  - `cpucaps_zone_get()`

## Scheduling Class Hooks

- `caps_sc_t`: per-thread scheduling-class CPU caps accounting, currently `csc_cputime`.
- `cpucaps_sc_init()`
- `cpucaps_charge()`: charges CPU time and optionally enforces.
- `CPUCAPS_CHARGE()` macro short-circuits when caps are off.
- `cpucaps_enforce()` / `CPUCAPS_ENFORCE()`: place capped threads on wait queues.
- `cpucaps_clock_callout`: hook into clock processing.

## Charge Modes

- `CPUCAPS_CHARGE_ENFORCE`
- `CPUCAPS_CHARGE_ONLY`

## Research Relevance

Important for resource controls, zones, projects, scheduling behavior, and CPU isolation effects on filesystem workloads.
