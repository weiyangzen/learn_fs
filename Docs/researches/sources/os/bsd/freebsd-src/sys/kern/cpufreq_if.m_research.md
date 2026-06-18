# File Research: sources/os/bsd/freebsd-src/sys/kern/cpufreq_if.m

## Summary
Defines the KObj `cpufreq` interface for CPU frequency policy and driver backends.

## Key Methods
- Policy-level methods: `set`, `get`, and `levels` operate on `struct cf_level`.
- Driver-level methods: `drv_set`, `drv_get`, `drv_settings`, and `drv_type` operate on `struct cf_setting` or driver type.

## Important Behavior
The interface separates aggregate CPU frequency levels from individual driver settings, allowing a cpufreq core to combine multiple providers.

## Risks
This file is an interface contract. Driver implementations must agree on units, priorities, level counts, and type semantics declared elsewhere in the cpufreq subsystem.
