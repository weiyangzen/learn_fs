# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_pm.c

## Role

`cpu_pm.c` implements platform-independent event-based CPU power management. It manages active power domains, power-management policy, domain state enumeration, state transitions, and an elastic utilization governor that reacts to dispatcher-reported domain utilization changes.

It is the policy layer between CMT/processor-group utilization tracking and platform-specific CPU power-state operations.

## Policy Model

The global `cpupm_policy` starts as `CPUPM_POLICY_DISABLED`. Supported policy behavior includes:

- `CPUPM_POLICY_DISABLED`: disables active power-aware dispatch support and forces active power domains to maximum performance.
- `CPUPM_POLICY_ELASTIC`: enables active power-aware dispatch support and allows domains to shift between max performance and low power based on utilization.

`cpupm_get_policy()` returns the active policy. `cpupm_set_policy()` changes policy under `cpu_lock`, pausing CPUs while changing the global policy so other CPUs cannot race with CPUPM state transitions.

## Domains and States

Power domains are represented by `cpupm_domain_t` records linked from `cpupm_domains`.

`cpupm_domain_find()` searches for an existing domain by ID and type. `cpupm_domain_create()` allocates and links a new domain.

`cpupm_domain_state_enum()` asks the platform layer how many states exist for a domain, allocates state storage, and asks the platform layer to fill it.

`cpupm_domain_init()` creates or finds the domain for a CPU and domain type. For active domains, it names the first enumerated state as `CPUPM_STATE_MAX_PERF` and the last as `CPUPM_STATE_LOW_POWER`, then assumes the domain begins at max performance.

`cpupm_domain_id()` delegates domain-ID discovery to `cpupm_plat_domain_id()`.

`cpupm_change_state()` delegates to `cpupm_plat_change_state()`, fires a `cpupm-change-state` DTrace probe, and updates the domain’s current state on success.

## Elastic Utilization Governor

`cpupm_utilization_event()` is the main event-driven policy function. It consumes dispatcher/CMT events for active power domains:

- `CPUPM_DOM_REMAIN_BUSY`
- `CPUPM_DOM_BUSY_FROM_IDLE`
- `CPUPM_DOM_IDLE_FROM_BUSY`

The simple target policy is “race to idle”:

- Busy domains should run at max performance.
- Idle domains should run at low power.

The governor prevents rapid state thrashing from transient work or transient idle periods. It tracks:

- `cpupm_ti_predict_interval`: transient idle threshold.
- `cpupm_tw_predict_interval`: transient work threshold.
- `cpupm_mispredict_thresh`: count needed to engage a governor.
- `cpupm_mispredict_gov_thresh`: count needed to remove a governor.
- Per-domain transient counters `cpd_ti` and `cpd_tw`.
- Per-domain governor mode: disengaged, transient-work governed, or transient-idle governed.

Transient work can suppress raising power; transient idle can suppress lowering power. Non-transient periods eventually remove the relevant governor.

## Global State Changes

`cpupm_state_change_global()` iterates all hardware power groups of the requested type and applies a named state to every CPU in each domain. Currently only active power domains are supported.

When policy is disabled, `cpupm_set_policy()` disables active PAD support and globally returns active power domains to max performance.

## Dynamic Max Performance Redefinition

`cpupm_redefine_max_activepwr_state()` lets platform code redefine which enumerated state is considered `CPUPM_STATE_MAX_PERF`. If the domain is currently at the old max-performance state, it immediately changes to the new max-performance state. Out-of-range indices are clamped to the lowest supported speed when multiple states exist.

## Governor Initialization

`cpupm_governor_initialize()` converts nanosecond tuning intervals into unscaled hrtime units, matching the timestamps passed to `cpupm_utilization_event()`.

Default transient idle and transient work governor intervals are both 400 microseconds.

## Dependencies

This file depends on:

- CMT power-aware dispatch: `cmt_pad_enable()` and `cmt_pad_disable()`.
- Processor-group hardware sets: `pghw_set_lookup()`, group iteration, `PG_CPU_ITR`.
- Platform CPUPM hooks: `cpupm_plat_domain_id()`, `cpupm_plat_state_enumerate()`, `cpupm_plat_change_state()`.
- Global CPU synchronization: `cpu_lock`, `pause_cpus()`, `start_cpus()`.
- DTrace probes for state changes and governor decisions.

## Research Notes

The key risk in this file is policy/state transition synchronization. Domain state can be changed by dispatcher-driven utilization events, global policy changes, and platform max-performance redefinition, so callers must respect the documented CPU-locking and pause semantics.
