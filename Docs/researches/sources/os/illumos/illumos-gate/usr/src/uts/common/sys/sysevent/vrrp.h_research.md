# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/vrrp.h

## Purpose
Defines VRRP sysevent publisher and payload attribute names for router state-change events.

## Main Interfaces
- `VRRP_EVENT_PUBLISHER`: publisher name, `vrrpd`.
- Attributes:
  - `VRRP_EVENT_VERSION`
  - `VRRP_EVENT_ROUTER_NAME`
  - `VRRP_EVENT_STATE`
  - `VRRP_EVENT_PREV_STATE`
- `VRRP_EVENT_CUR_VERSION`.

## Dependencies And Relationships
Schema comments target VRRP events, especially `ESC_VRRP_STATE_CHANGE` under the VRRP sysevent class.

## Research Notes
This header defines the payload vocabulary only; state value meanings come from the VRRP daemon/domain logic.
