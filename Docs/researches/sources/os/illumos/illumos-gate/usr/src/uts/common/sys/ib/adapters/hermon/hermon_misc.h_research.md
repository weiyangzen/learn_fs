# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_misc.h

## Purpose
Defines miscellaneous Hermon driver support: address handles, multicast, protection domains, queue allocation, doorbell records, user doorbell pages, port limits, kstats, 32-bit ioctl compatibility, loopback test state, Fast Memory Registration pools, and associated prototypes.

## Main Interfaces
- Address handle and multicast defaults:
  - `HERMON_NUM_AH_SHIFT`, `HERMON_UDAV_SIZE_SHIFT`
  - UDAV sync decision macro.
  - address-path type flags for QP vs UDAV formats.
  - multicast group sizing, hash sizing, MGID validation constants, and QP-list pointer macro.
- Protection/domain/port defaults:
  - PD, PKey, GID, UAR, MTU, port width, VL, and counter constants.
- Doorbell support:
  - `hermon_dbr_t`
  - `hermon_dbr_info_t`
  - per-page DBR count and bitmap helpers.
  - user DBR page and management structs.
- Software handles:
  - `struct hermon_sw_ah_s`
  - `struct hermon_sw_mcg_list_s`
  - `struct hermon_sw_pd_s`
  - `struct hermon_qalloc_info_s`
- Kstats:
  - `hermon_ks_mask_t`
  - 64-bit perf counter index enum.
  - `hermon_perfcntr64_ks_info_t`
  - `hermon_ks_info_t`
- 32-bit ioctl compatibility:
  - `hermon_ports_ioctl32_t`
  - `hermon_loopback_ioctl32_t`
  - `hermon_flash_ioctl32_t`
- VTS loopback:
  - `hermon_loopback_comm_t`
  - `hermon_loopback_state_t`
- FMR:
  - `hermon_fmr_list_t`
  - `struct hermon_sw_fmr_s`
  - `HERMON_FMR_MAX_REMAPS`
- Prototypes cover DBR allocation/free, FMR pools, address handles, multicast attach/detach, PD allocation/refcounts, port query/modify, kstat init/fini, address-path translation, validation helpers, and queue allocation/free.

## Dependencies And Relationships
Includes `hermon_typedef.h`, `hermon_ioctl.h`, `hermon_rsrc.h`, and `hermon_hw.h`. This is a broad support header used by CQ, QP, MR, ioctl, statistics, multicast, and port code.

## Research Notes
The file bridges user-facing diagnostics and core IB verbs support. Lock annotations define which handle fields are immutable, lock-protected, or intentionally readable without locks.
