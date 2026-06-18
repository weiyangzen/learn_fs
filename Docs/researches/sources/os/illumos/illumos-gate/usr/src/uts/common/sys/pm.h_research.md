# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pm.h

## Purpose
Defines the user/kernel power-management ioctl command set, request payloads, state-change notifications, and 32-bit structure mirrors.

## Main Interfaces
- `pm_cmds`: power-management commands, including many obsolete commands plus current component threshold, current/full power, dependency, CPU power management, S3/autos3, and CPU deep-idle controls.
- Compatibility aliases:
  - `PM_GET_POWER`
  - `PM_SET_POWER`
- Request structures:
  - obsolete `pm_request`
  - `pm_req_t`
  - `pm_searchargs_t`
- Dependency aliases:
  - `pmreq_keeper`
  - `pmreq_kept`
- State-change interface:
  - `psc_events`
  - `PSC_EVENT_LOST`
  - `PSC_ALL_LOWEST`
  - `PM_LEVEL_UNKNOWN`
  - `pm_state_change_t`
- 32-bit kernel views:
  - `pm_request32`
  - `pm_req32_t`
  - `pm_state_change32_t`
  - `pm_searchargs32_t`
- `pm_states`: return values describing PM enabled/disabled, thresholds, direct management, CPU PM, autos3, and S3 support states.

## Dependencies And Relationships
Includes `sys/types.h`. The header is a public ioctl ABI consumed by PM tools and handled by kernel PM code.

## Research Notes
Several commands and structures are explicitly documented as obsolete or test-only. `pm_state_change_t` orders `event` and `flags` differently by endianness to preserve layout semantics.
