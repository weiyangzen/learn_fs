# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpu_pm.h

## Role

Defines CPU power manager policies, domain state, governor state, utilization events, and platform hooks.

## Key Types

- `cpupm_policy_t`: `CPUPM_POLICY_ELASTIC`, `CPUPM_POLICY_DISABLED`.
- `cpupm_dtype_t`: active and idle power domains.
- `cpupm_state_name_t`: named low-power and max-performance states.
- `cpupm_gov_state_t`: transience governor states.
- `cpupm_util_event_t`: dispatcher utilization events.
- `cpupm_handle_t`: platform handle.
- `cpupm_state_t`: speed plus platform handle.
- `cpupm_domain_t`: domain id/type, state array/current state, named states, raise/lower timestamps, transient histories, governor state, and linked-list pointer.

## Interfaces

- Domain management:
  - `cpupm_domain_init()`
  - `cpupm_domain_id()`
  - `cpupm_change_state()`
  - `cpupm_redefine_max_activepwr_state()`
- Policy:
  - `cpupm_set_policy()`
  - `cpupm_get_policy()`
  - `cpupm_utilization_event()`
- Platform driver hooks:
  - `cpupm_plat_domain_id()`
  - `cpupm_plat_state_enumerate()`
  - `cpupm_plat_change_state()`

## Scope

Definitions are visible when `_KERNEL` or `_KMEMUSER` is defined.

## Research Relevance

Documents the higher-level CPU power manager model used by dispatcher/utilization signals and platform-specific state transitions.
