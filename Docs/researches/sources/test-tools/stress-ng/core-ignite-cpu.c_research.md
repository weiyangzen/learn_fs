# sources/test-tools/stress-ng/core-ignite-cpu.c

## Purpose

This module implements the optional CPU ignition feature, which tries to push CPUs into maximum-performance settings during a stress run and then restore original settings. It manipulates Linux CPU frequency, governor, energy-performance-bias, resume-latency, Intel P-state, cpufreq boost, and `/dev/cpu_dma_latency` controls when available.

## Important APIs, Types, And Functions

`stress_settings_t` describes global sysfs controls with default maximizing values and saved originals. `stress_cpu_setting_t` records per-CPU frequency limits, resume latency, governor, energy performance bias, and a flag mask indicating which controls are usable. Public APIs are `stress_ignite_cpu_start` and `stress_ignite_cpu_stop`; `stress_ignite_cpu_set` applies or restores per-CPU settings and clears flag bits for controls that fail.

## Control Flow

`stress_ignite_cpu_start` opens `/dev/cpu_dma_latency` and writes zero latency if possible, discovers configured CPUs, allocates per-CPU setting storage, reads cpufreq and power-control files, applies global maximizing sysfs settings, saves originals, and forks a child daemon. The child sets parent-death alarm and process name, then once per second reapplies global settings and per-CPU max-frequency/performance settings while `stress_continue_flag()` remains true.

`stress_ignite_cpu_stop` closes the latency fd, kills and waits for the child, restores per-CPU settings using saved values, frees CPU state, restores global sysfs settings, and clears `enabled`.

## State And Persistence Behavior

State is global and process-lifetime scoped: `cpu_settings`, `pid`, `enabled`, `max_cpus`, and `latency_fd`. It also temporarily mutates persistent kernel/sysfs tunables and must restore saved values on stop. If start returns early after partial changes or the process is killed without stop, system settings could remain modified.

## Dependencies And Integration Points

The module depends on filesystem read/write helpers, configured CPU count, parent-death alarm, process naming, random governor choice, global continue flag, and kill/wait helpers. It is Linux/sysfs oriented, with x86-specific global settings for Intel P-state.

## Risks And Test Signals

Risks are high because it writes power-management controls. Permission failures, missing sysfs files, hotplugged CPUs, malformed sysfs values, and incomplete restoration are key edge cases. Test signals include no-op behavior without writable controls, restoration after start/stop, child death on parent exit, correct cleanup of saved setting allocations, and no repeated logging for expected permission failures.
