# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_cfg.h

## Purpose
Defines the Hermon driver configuration profile, including resource sizing, port capabilities, mailbox counts, management-agent choices, command polling timing, interrupt preference, IOMMU bypass policy, relaxed ordering flags, and optional GUID overrides.

## Main Interfaces
- `hermon_cfg_profile_t`: central in-memory configuration record used by the driver after attach-time profile initialization.
- Constants:
  - `HERMON_RO_DISABLED`, `HERMON_RO_ENABLED` for PCIe relaxed ordering.
  - `HERMON_CFG_MEMFREE` profile selector.
  - `HERMON_MAX_PORTS` fixed at 2.
  - `HERMON_LOG_CMPT_PER_TYPE` default control MPT allocation size.
- Lifecycle prototypes:
  - `hermon_cfg_profile_init_phase1()`
  - `hermon_cfg_profile_init_phase2()`
  - `hermon_cfg_profile_fini()`

## Dependencies And Relationships
This header relies on `hermon_state_t` being declared before use by includers. The profile fields are consumed across QP, CQ, SRQ, MR, event queue, multicast, mailbox, and port initialization code.

## Research Notes
This is a driver policy header rather than hardware layout. It captures tunables that gate nearly every resource table size used later by command and resource initialization.
