# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_nodeid.c

## Role

`ddi_nodeid.c` implements DDI node ID management. It allocates, frees, and reserves integer node IDs for devinfo nodes using a sorted free-list of available ranges.

The managed range is `1 .. 0x10000000`. Values `0`, `DEVI_PSEUDO_NODEID`, and `DEVI_SID_NODEID` are illegal. The low numeric range is chosen to avoid overlap with PROM node IDs, even though the code can handle a broader 32-bit range.

## Data Structure

The free list consists of `struct available` range records:
- `nodeid` is the first free ID in the range;
- `count` is the number of consecutive free IDs;
- `next`/`prev` link records in sorted order.

The allocator starts with one seed range copied into heap memory during `impl_ddi_init_nodeid()`. A single global mutex, `nodeid_lock`, protects the list.

## Allocation and Freeing

`impl_ddi_alloc_nodeid()` takes the first ID from the head range without allocating memory. It advances the range start and decrements count, unlinking and freeing the range after dropping the lock if it becomes empty. It returns `DDI_FAILURE` and `*nodeid = 0` when no IDs remain.

`impl_ddi_free_nodeid()` allocates a potential new range before taking the lock, then reinserts the freed ID into the sorted list. It handles four cases:
- extend the beginning of an existing range;
- extend the end of an existing range and coalesce with the next range if adjacent;
- insert a one-ID range before the next higher range;
- append a one-ID range at the end.

If the freed ID already lies inside a free range, the function panics because that means a duplicate free.

## Reserving Existing IDs

`impl_ddi_take_nodeid()` removes a specified ID from the free list, usually to reserve an externally supplied node ID. IDs outside the managed range are treated as successfully reserved because this allocator does not own them.

Within a free range, the function can:
- take the first ID by advancing the range;
- take the last ID by decrementing count;
- take a middle ID by splitting the range into two records.

The middle-split case needs a preallocated range record. If called with `KM_NOSLEEP` and allocation fails, it returns `-1`; otherwise success is `0`. If the ID is not found in the free list, the function logs that uniqueness may not be guaranteed but still returns success.

## Subset Relevance

Node IDs are part of the devinfo tree identity layer. Filesystem and storage drivers appear as devinfo nodes and depend indirectly on stable allocation/reservation of these IDs during device enumeration.
