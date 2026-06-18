# File Research: sources/os/linux/linux/mm/page_ext.c

Infrastructure for optional per-page extension storage outside `struct page`. It allows debug/accounting features to attach per-page metadata without permanently enlarging the base page structure.

Key responsibilities:
- Collects `page_ext_operations` users such as page owner, page idle flags on 32-bit, allocation profiling tags, page table checks, and IOMMU debug page allocation.
- Determines at boot whether page extension storage is needed through each client’s `need()` callback.
- Computes `page_ext_size`, assigns client offsets, and invokes optional init callbacks once storage exists.
- Allocates and looks up page extension arrays for flatmem and sparsemem configurations.
- Handles sparsemem memory hotplug by allocating page extension storage on memory online and invalidating/freeing it on offline.
- Exposes lookup APIs: `page_ext_lookup()`, `page_ext_get()`, `page_ext_from_phys()`, and `page_ext_put()`.

Important behavior:
- `early_page_ext` can be forced by the `early_page_ext` boot parameter and defaults on for allocation-profiling debug builds.
- If any client requires shared flags, the base `struct page_ext` is included before client-specific offset storage.
- Flatmem allocates one table per node through memblock during boot; misaligned node ranges get extra space so buddy checks around node boundaries are safe.
- Sparsemem stores a section-relative base pointer in `mem_section->page_ext`, computed as `base - page_ext_size * section_start_pfn`.
- Sparsemem offline invalidates section `page_ext` pointers first, waits for an RCU grace period, then frees the underlying storage to avoid use-after-free.
- `page_ext_get()` enters an RCU read-side critical section and returns a pointer that remains valid until `page_ext_put()`.
- `page_ext_from_phys()` rejects MMIO, zone-device, holes, and offline memory by requiring `pfn_to_online_page()`.

Dependencies:
- Uses memory model APIs, memblock, sparsemem sections, memory hotplug notifiers, RCU, vmalloc, exact-page allocation, kmemleak, page owner, page idle, page table check, allocation profiling, and IOMMU debug page allocation.
- Lookup callers must hold RCU directly or use `page_ext_get()`/`page_ext_put()`.

Notable risks:
- Sparsemem stores tagged invalid pointers using `PAGE_EXT_INVALID`; users must route through the helpers instead of dereferencing section state directly.
- Page allocator sanity checks can run before page_ext arrays exist during boot or hotplug, so lookup can legitimately return NULL.
- Hotplug teardown correctness depends on invalidation before `synchronize_rcu()` and only freeing after readers finish.
- `page_ext_get()` callers must not sleep until `page_ext_put()` releases the RCU read lock.
