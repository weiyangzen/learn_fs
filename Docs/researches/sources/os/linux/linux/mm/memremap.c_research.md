# File Research: sources/os/linux/linux/mm/memremap.c

## Purpose

Implements `memremap_pages()` and related helpers for mapping device-managed physical address ranges into the kernel memory model with `struct page` backing, primarily for ZONE_DEVICE users such as device-private memory, coherent device memory, fs-dax, generic device memory, and PCI peer-to-peer DMA memory.

## Core State

The file maintains a global `pgmap_array` xarray mapping PFNs to `struct dev_pagemap` objects. Lookup is RCU-protected and references are taken through the pagemap percpu ref.

`dev_pagemap` ranges may include altmap-backed vmemmap storage. `pfn_first()`, `pfn_end()`, `pfn_len()`, and `pgmap_pfn_valid()` compute usable PFN coverage while accounting for altmap-reserved vmemmap pages.

## Mapping Flow

`memremap_pages()` validates the pagemap, initializes its completion and percpu ref, then maps each range through `pagemap_range()`.

`pagemap_range()` performs the main work:

1. Reject conflicting dev_pagemap mappings at range boundaries.
2. Reject ranges that intersect System RAM.
3. Store the pagemap in `pgmap_array`.
4. Track the PFN map with `pfnmap_track()`.
5. Validate hotplug addressability with `mhp_range_allowed()`.
6. Acquire `mem_hotplug_lock`.
7. Add struct page backing with `add_pages()` for private memory or `arch_add_memory()` for CPU-accessible memory.
8. Add KASAN zero shadow for CPU-accessible memory.
9. Move the range into ZONE_DEVICE.
10. Release the hotplug lock.
11. Initialize ZONE_DEVICE memmap entries with `memmap_init_zone_device()`.
12. Preload pagemap references for relevant device-memory types.

Device-private memory intentionally avoids a linear mapping. Other device memory types use architecture memory-add paths.

## Unmapping Flow

`memunmap_pages()` kills the pagemap percpu ref, drops preloaded references for applicable types, waits for completion, unmaps each range with `pageunmap_range()`, exits the percpu ref, and warns if altmap pages remain allocated.

`pageunmap_range()` removes the PFN range from its zone, removes sparse pages or architecture linear mappings depending on memory type, removes KASAN shadow, untracks the PFN map, and deletes `pgmap_array` entries after RCU synchronization.

Device-managed wrappers:

- `devm_memremap_pages()`
- `devm_memunmap_pages()`

bind unmapping to device resource lifetime.

## Pagemap Lookup and Page Freeing

`get_dev_pagemap()` looks up a pagemap by PFN and attempts to acquire a live percpu reference.

`free_zone_device_folio()` handles release of ZONE_DEVICE folios:

- uncharges memory cgroups;
- clears anonymous exclusive state;
- clears stale mappings for non-fsdax/non-generic types;
- invokes driver `folio_free()` for private, coherent, and P2PDMA pages;
- resets generic page refcount for reuse;
- wakes fs-dax waiters;
- drops pagemap references where required.

`zone_device_page_init()` prepares a ZONE_DEVICE page or compound folio for driver allocation, clears stale compound metadata, assigns `pgmap`, resets fs-dax share state, takes pagemap references, sets refcount, locks the page, and prepares compound page metadata for higher orders.

## Device Type Handling

`memremap_pages()` validates type-specific requirements:

- `MEMORY_DEVICE_PRIVATE` requires `CONFIG_DEVICE_PRIVATE`, `migrate_to_ram`, `folio_free`, and `owner`.
- `MEMORY_DEVICE_COHERENT` requires `folio_free` and `owner`.
- `MEMORY_DEVICE_FS_DAX` uses decrypted page protections.
- `MEMORY_DEVICE_GENERIC` uses default protections.
- `MEMORY_DEVICE_PCI_P2PDMA` uses noncached protections.

## Integration Points

This file integrates with memory hotplug, sparsemem, ZONE_DEVICE, devres, KASAN, pfnmap tracking, percpu refs, xarray lookup, memory cgroups, swap/migration semantics, and architecture add/remove memory hooks.

## Risks and Invariants

Ranges must not overlap System RAM or existing dev_pagemap sections. Altmap support is limited to a single range. The pagemap xarray must be unwound on all failures. Refcount shutdown must wait for all outstanding device page users before tearing down memmap and mappings. ZONE_DEVICE page reinitialization must clear stale compound and mapping state before reuse.
