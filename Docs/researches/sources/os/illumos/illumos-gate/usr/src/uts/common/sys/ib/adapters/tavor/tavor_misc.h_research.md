# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_misc.h

## Role

`tavor_misc.h` collects Tavor support contracts for address handles, multicast groups, protection domains, queue allocation, port operations, kstats, VTS loopback support, and ioctl compatibility structures.

## Major Definitions

The header defines AH/UDAV counts and size, minimal AH profile, and `TAVOR_UDAV_IS_SYNC_REQ()`. Address-path type constants distinguish QP paths from UDAV paths.

Multicast definitions include MCG counts, QPs per group, MCG entry sizing and QP-list pointer macros, multicast hash sizing, and IBA-derived multicast GID validation fields for top bits, permanent/non-permanent flags, and scope. PD, PKey table, GID table, UAR page, MTU, port width, VL capability, and kstat counter constants follow.

Queue allocation location constants distinguish normal kernel memory, user-mappable memory, and HCA DDR. `TAVOR_VTS_LOOPBACK_MIN_WAIT_DUR` sets a minimum loopback polling delay.

Software structures include:
- `tavor_sw_ah_s` for AH/UDAV resources, PD/MR handles, saved GUID/rate, and sync state.
- `tavor_sw_mcg_list_s` for the shadow multicast table.
- `tavor_sw_pd_s` for PD number, reference count, and resource handle.
- `tavor_qalloc_info_s` for queue allocation size, alignment, buffer pointers, location, DMA/access handles, and user-memory cookie.
- kstat mask and 64-bit performance counter state.
- 32-bit ioctl compatibility structures for ports, loopback, and flash.
- VTS loopback communication and test-state structures.

## Interfaces

The file declares AH allocate/free/query/modify, multicast attach/detach, PD allocate/free/refcount, port query/modify, kstat init/fini, address-path set/get, port/PKey validation, queue allocate/free, and DMA attribute initialization.

## Integration Notes

This header is a broad support layer used by data-path setup, management operations, user ABI handling, diagnostics, and statistics. Its queue-location constants influence DMA sync and userland mapping behavior elsewhere.
