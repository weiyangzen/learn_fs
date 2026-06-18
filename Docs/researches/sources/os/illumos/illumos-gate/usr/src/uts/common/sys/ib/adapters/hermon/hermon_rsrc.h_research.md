# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_rsrc.h

## Role

`hermon_rsrc.h` defines the resource-management contract for the illumos Hermon InfiniBand HCA driver. It names Hermon resource pools, classifies hardware and software resource types, describes initialization/cleanup state, and declares the allocation/free/reservation entry points used across the driver.

## Major Definitions

The header defines sleep-context constants and `HERMON_SLEEPFLAG_FOR_CONTEXT()`, which maps interrupt or panic context to non-sleeping allocation behavior. It also defines resource cache and vmem arena names for ICM, mailboxes, CMPT/QPC/SRQC/CQC/EQC/DMPT/MTT/MCG tables, UAR pages, BlueFlame pages, and software handle caches.

The main enums are:
- `hermon_mpt_rsrc_type_t`, classifying CMPT-backed MPT/control resource variants.
- `hermon_rsrc_type_t`, enumerating all ICM-backed and non-ICM resources, including FCoIB-related QPC reservations.
- `hermon_rsrc_cleanup_level_t`, a staged attach/detach cleanup ladder.

The initialization helper structures describe mailbox pools, hardware entry pools, and software handle pools. `hermon_rsrc_pool_info_s` records each resource pool’s type, location, size, alignment, quantum, vmem arena, driver state, and private metadata. `hermon_rsrc_priv_mbox_t` carries DMA/access attributes for mailbox resources. `hermon_rsrc_s` is the allocation handle returned to consumers, with address, length, index, DMA handle, and access handle fields.

## Interfaces

The exported functions are `hermon_rsrc_alloc`, `hermon_rsrc_free`, two-phase resource initialization, resource finalization by cleanup level, and `hermon_rsrc_reserve` for FCoIB reservation use.

## Integration Notes

This header is central to Hermon attach, detach, firmware table setup, mailbox setup, and fast-path object allocation. Resource enum order is significant because resource arrays are indexed by type and comments explicitly constrain where new ICM resources can be inserted.
