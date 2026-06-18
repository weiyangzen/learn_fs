# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/ibd/ibd.h

## Purpose

Defines the private IP-over-InfiniBand (`ibd`) driver interface and state. It covers UD and Reliable Connected modes, driver lifecycle flags, tunables, multicast/address-handle cache rules, IPoIB wire headers, work queue objects, LSO/copy buffers, per-port state, RC connection/channel state, global service registration state, and cross-file prototypes.

## Main Definitions

- CQ polling flags, maximum receive mblk chain length, send batching limit, resource reap masks, async request opcodes, and attach/start state flags.
- Tunable defaults and bounds for UD/RC link mode, LSO policy, copy thresholds, WQE counts, AH/hash sizes, completion coalescing, SRQ enablement, SRQ sizes, and RC thresholds.
- Thresholds for LSO buffers, SWQEs, and TX CQ polling.
- Extensive multicast/AH cache design comments covering active/free list transitions, multicast disable, MCG delete/create traps, promiscuous rejoin, unreliable traps, and sendonly/fullmember behavior.
- Atomic AH reference/recycle-bit macros using high bits in `ac_ref`.
- Active/free address-handle cache list/hash macros.
- `IBD_PAD_NSNA()` adjusts IPv6 Neighbor Solicitation/Advertisement link-layer address padding between Solaris IP expectations and IPoIB alignment.
- IPoIB header/address/pseudo-TX-header and pseudo-GRH structures.
- RC mode service IDs, including legacy OFED interop ID.
- Kernel-only definitions:
  - RC channel state enum.
  - Async request, multicast cache, address cache, WQE, SWQE/RWQE, generic list, LSO bucket, RX post queue, and large-buffer structures.
  - `ibd_state_t`: main per-interface state with IBT/MAC handles, TX/RX lists, CQs, UD channel, multicast group info, MAC addresses/GIDs, async request thread, AH/multicast caches, trap/link/MAC state, counters, checksum/LSO capabilities, RC mode configuration, RC listeners, channel lists, SRQ, large TX buffers, chained receive state, timeout state, RC statistics, device identity, and all UD/RC tunables.
  - Global IBTF state and service list structures.
  - RC hello message and `ibd_rc_chan_t` with channel handle, state, ACE, TX/RX WQE lists, CQs, soft interrupts, chained send/receive, channel role, timeout/use markers, and close synchronization.
- Prototypes shared between `ibd.c` and `ibd_cm.c` for warnings, memory unmapping, async work queueing, AH cache lookup/recycle/refcount, RC listen/connect/close, SRQ handling, RC send/receive resources, config, and stats.

## Integration Notes

This header is central to the illumos IPoIB MAC driver. It bridges MAC provider APIs, IBT channels/CQs/MRs, multicast SA membership, address resolution, and optional RC connections.

## Risks and Gotchas

- The address-handle cache deliberately avoids locking active-list operations except via async-thread ownership and atomic refcounts; changing caller context can break this model.
- Multicast trap handling is conservative because SA traps are unreliable and out of order.
- RC mode has separate active/passive channel states, two service IDs, optional SRQ, timeout reaping, and large-copy-buffer fallback.
- Tunables interact with HCA limits and CQ sizes; comments call out catastrophic errors if SRQ buffers exceed RWQE constraints.
- `RX_QUEUE_CACHE_LINE` depends on exact struct size and may need revision if fields change.
