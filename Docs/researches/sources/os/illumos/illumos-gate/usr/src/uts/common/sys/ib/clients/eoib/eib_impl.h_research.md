# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/eib_impl.h

## Purpose

Defines the private implementation surface for the EoIB leaf driver: constants, debug controls, service-thread names, WQE pools, LSO buffers, admin/control/data channel sizing, multicast GID layouts, gateway and port properties, vNIC/vHUB tables, per-instance state, and cross-file function prototypes.

## Main Definitions

- Driver return codes, max line/SGL/posting/payload constants, copy threshold, max vNICs, timeouts, retry limits, and GRH size.
- Debug flag masks and logging macros, with debug categories compiled out unless `EIB_DEBUG` is set.
- Service-thread names for event handling, receive-WQE refill, vNIC creation, TX-WQE monitoring, and LSO-buffer monitoring.
- `EIB_FIND_LSB_SET()` lookup macro used by bitmap WQE allocation.
- LSO buffer bucket structures and status flags.
- Admin, control, and data QP sizing constants and CQ moderation defaults.
- WQE `qe_info` bit packing for block, index, type, and flags.
- `eib_wqe_t`: send/receive WQE wrapper with copy buffers, payload header, UD destination, free routine, mblk, memory I/O handle, IBT WR, SGLs, post chain, and channel pointer.
- Two-level bitmap WQE pool model: 64 WQEs per block, 64 blocks per pool.
- WQE low/high-water marks and priority constants.
- `eib_mgid_spec_t`/`eib_mgid_t`: multicast GID layout for vHUB data/update/table groups.
- Gateway, port, HCA capability, multicast group, channel, login-data, vHUB map/table/update, Ethernet header, vNIC, node state, stats, address-vector cache, event, vNIC request, keepalive, and main `eib_t` state structures.
- Function prototypes for FIP, service threads, admin/control/data QPs, resources, IBT, channels, MAC layer, vNIC handling, logging, properties, globals, and hardware workarounds.

## Integration Notes

`eib_t` is the leaf driver's main soft state and ties together IBT handles, MAC registration, gateway properties, admin QP, shared WQE pools, LSO buffers, vNIC slots, event queues, refiller/creator/monitor/keepalive threads, and address-vector cache.

## Risks and Gotchas

- Many structures use multiple mutex/condition-variable pairs; vNIC creation/deletion is serialized separately from active/zombie/rejoin bitmaps.
- WQE allocation depends on 64-bit bitmap invariants; constants say `EIB_WQES_PER_BLK` must not change.
- Data path uses large SGL arrays and LSO copy buffers to work around HCA SGL limits.
- Several runtime workaround globals disable descriptor length, checksum offload, LSO, multicast entries, AV discovery, VP flag, or vHUB checksum assumptions.
