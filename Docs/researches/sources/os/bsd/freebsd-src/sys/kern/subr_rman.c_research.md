# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_rman.c

## Purpose

`subr_rman.c` implements FreeBSD’s kernel resource manager for bus and CPU resource ranges. It tracks allocatable hardware-like resources such as I/O ports, memory windows, IRQs, and other indexed ranges. The implementation is for `RMAN_ARRAY` style resources; `RMAN_GAUGE` is explicitly unimplemented.

The manager does not discover or assign hardware by itself. Bus and architecture code use it to manage ranges, and device drivers request allocations through those higher-level layers.

## Main Data Model

Internal resources are `struct resource_i`, which wraps the public `struct resource` and adds:

- `r_start`, `r_end`: inclusive resource range.
- `r_flags`: allocation/share/active flags.
- `r_virtual`, `r_irq_cookie`: mapping and interrupt metadata.
- `r_dev`: owning device.
- `r_rm`: parent resource manager.
- `r_rid`, `r_type`: optional resource ID/type.
- `r_link`: ordered list link in `rm->rm_list`.
- `r_sharelink`, `r_sharehead`: support exact-range shared allocations.

The public `struct resource` stores a back-pointer in `__r_i`.

All initialized resource managers are linked from global `rman_head`, protected by `rman_mtx`. Each manager has its own `rm_mtx`.

## Initialization And Region Management

`rman_init()` validates type, sets a default full end range if start/end are both zero, initializes the manager list and mutex, and inserts the manager into the global list.

`rman_manage_region(rm, start, end)` adds a free region to the manager. The list remains sorted and adjacent free regions are merged when possible. It rejects ranges outside the manager bounds or overlapping existing ranges.

`rman_init_from_resource()` initializes a manager and manages the exact range from an existing resource.

`rman_fini()` refuses to finalize if any resource is allocated, frees all remaining free entries, removes the manager from the global list, and destroys its mutex.

`rman_first_free_region()` and `rman_last_free_region()` scan the list for the first or last unallocated entry.

## Allocation, Adjustment, And Release

`rman_reserve_resource(rm, start, end, count, flags, dev)` is the core allocator. It:

- Validates nonzero count and flags.
- Computes alignment from `RF_ALIGNMENT(flags)`.
- Searches free regions for a compatible aligned subrange.
- Splits free entries into two or three pieces when allocating from the middle.
- Marks the allocated entry with `RF_ALLOCATED` and caller flags.
- If no unshared region fits and `RF_SHAREABLE` is set, searches for an exact-size compatible shared region.

Shared resources must match exact range length and sharing type (`RF_SHAREABLE | RF_PREFETCHABLE`). The first shared resource owns the list entry and gets `RF_FIRSTSHARE`; additional sharers are separately allocated `resource_i` objects linked on the share list.

`rman_adjust_resource(rr, start, end)` shrinks or extends an allocated resource while preserving at least some overlap with the original range. It does not support shared resources. Growth requires adjacent free space; shrinking may create new free entries before or after the resource.

`int_rman_release_resource()` releases an allocated resource. It clears `RF_ACTIVE`, handles shared-list removal and first-share reassignment, then merges the released range with adjacent free regions where possible. If no merge is possible, the same entry becomes a free region in place. `rman_release_resource()` wraps it with manager locking.

`rman_activate_resource()` and `rman_deactivate_resource()` set or clear `RF_ACTIVE`.

## Metadata Accessors

The file provides getters/setters for resource start/end/size/flags, virtual address, IRQ cookie, bus tag, bus handle, `resource_map`, RID, type, owning device, and manager membership. `rman_make_alignment_flags()` converts a size to the corresponding alignment-log flags.

## Sysctl And Debugging

`sysctl_rman()` exposes resource-manager and resource entries through `hw.bus.rman`. It supports querying manager metadata with resource index `-1`, or individual resources including shared resources.

DDB commands provide:

- `show rman <addr>`: dump one manager.
- `show rmans`: list manager headers.
- `show allrman` / `show all rman`: dump all managers and entries.

## Dependencies

This file depends on the bus/device layer, `sys/rman.h`, mutexes, sysctl, DDB, and machine bus-space types.

## Invariants And Constraints

The resource list is sorted by range and represents both free and allocated spans. Free spans are merged eagerly. Allocated spans are not allowed to partially overlap. Shared allocations are only permitted for exact same range and compatible sharing flags.

Range endpoints are inclusive, so size is always `end - start + 1`. Overflow-sensitive paths check for wrap around `RM_MAX_END` and alignment masks.

## Maintenance Notes

This is shared infrastructure with significant locking and list-shaping complexity. Any change to allocation or release must preserve:

- Sorted list order.
- No overlapping non-shared resources.
- Correct free-region coalescing.
- Exact handling of shared first-owner replacement.
- No sleeping allocation while holding manager locks unless already established by the existing code path.
