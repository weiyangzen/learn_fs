# File Research: sources/os/linux/linux/mm/kfence/kfence.h

## Role

Internal KFENCE header shared by core allocation/fault logic and report generation.

## Key Definitions

- `KFENCE_CANARY_PATTERN_U8(addr)` and `KFENCE_CANARY_PATTERN_U64` define address-varied canary patterns.
- `KFENCE_STACK_DEPTH` sets report stack depth to 64.
- `enum kfence_object_state` tracks unused, allocated, RCU-freeing, and freed objects.
- `struct kfence_track` stores pid, CPU, timestamp, stack depth, and stack entries.
- `struct kfence_metadata` records freelist/RCU nodes, state lock, object address, size, cache, one unprotected page, alloc/free tracks, allocation stack hash, and optional memcg object extension data.
- `KFENCE_METADATA_SIZE` rounds the metadata array to pages.
- `addr_to_metadata()` maps a pool address to its guarded-object metadata and rejects non-KFENCE or edge addresses.
- `enum kfence_error_type` enumerates out-of-bounds, use-after-free, canary corruption, invalid access, and invalid free.
- `enum kfence_fault` defines report/oops/panic handling policy.

## API Surface

Declares shared globals and functions:

- `kfence_enabled`
- `kfence_freelist_lock`
- `kfence_metadata`
- `kfence_report_error()`
- `kfence_handle_fault()`
- `kfence_print_object()`

## Dependencies

Includes Linux `mm`, `slab`, `spinlock`, and slab internals for `struct kmem_cache`.

## Research Notes

The metadata lock annotation is central: allocation, free, and page-fault reporting can race on the same metadata. `addr_to_metadata()` encodes the pool layout assumption that object pages and guard pages alternate.
