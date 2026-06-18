# File Research: sources/os/linux/linux/mm/migrate_device.c

## Role

`migrate_device.c` implements HMM/ZONE_DEVICE migration between CPU-addressable system memory and device private/coherent memory. It exposes the `migrate_vma_*` API for drivers that migrate a virtual address range, plus PFN-range helpers for migrating device memory back to normal memory without walking a VMA.

## Main Responsibilities

- Walk CPU page tables for a VMA range and collect source PFNs into `migrate->src`.
- Replace CPU PTEs/PMDs with migration entries while pages are locked and pinned.
- Support anonymous holes so drivers can populate device memory for previously unallocated anonymous addresses.
- Support device-private and device-coherent page selection by `pgmap_owner`.
- Coordinate invalidation through MMU notifiers before and after page table collection/insertion.
- Move struct-page metadata from source to destination pages with the generic migration helpers in `migrate.c`.
- Finalize migration by restoring CPU mappings to the destination or source pages and releasing locks/references.

## Key Entry Points

- `migrate_vma_setup()`: validates `struct migrate_vma`, clears arrays, walks page tables, collects candidates, and unmaps migratable pages.
- `migrate_vma_pages()`: migrates source struct-page metadata to destination pages supplied by the driver.
- `migrate_vma_finalize()`: restores CPU page tables and unlocks/puts source and destination folios.
- `migrate_device_pages()`: metadata migration for pre-collected device PFN arrays.
- `migrate_device_finalize()`: finalization for `migrate_device_pages()`.
- `migrate_device_range()`: prepares a contiguous device PFN range for migration to system memory.
- `migrate_device_pfns()`: prepares a non-contiguous pre-populated device PFN array.
- `migrate_device_coherent_folio()`: migrates a single device-coherent folio back to normal memory.

## VMA Range Collection

`migrate_vma_collect()` wraps the page-table walk in `MMU_NOTIFY_MIGRATE` invalidation. The walk callbacks record one source entry per page-sized slot. `migrate_vma_collect_hole()` marks anonymous holes as migratable and optionally marks PMD-sized compound holes. `migrate_vma_collect_pmd()` handles ordinary PTEs, device-private swap entries, device-coherent pages, zero pages, and large folio splitting. It installs migration entries immediately when it can lock the folio, preserving write, young, dirty, soft-dirty, uffd-wp, and anon-exclusive state.

For PMD-mapped THPs, `migrate_vma_collect_huge_pmd()` can collect and replace the whole PMD with a migration entry when `MIGRATE_VMA_SELECT_COMPOUND` is requested and alignment permits. Otherwise it falls back to splitting.

## Unmap and Pin Checks

`migrate_device_unmap()` isolates non-device folios from the LRU, uses `try_to_migrate()` for still-mapped folios, and rejects pages that remain mapped or appear pinned. `migrate_vma_check_page()` applies a refcount-vs-mapcount heuristic similar to generic migration but accounts for the caller’s extra reference and ZONE_DEVICE extra references. Rejected pages have migration entries restored and are unlocked/put.

## Metadata Migration

`__migrate_device_pages()` iterates `src_pfns` and `dst_pfns`:

- If the source is a hole and destination is valid, it inserts a new anonymous page or device-private entry through `migrate_vma_insert_page()`.
- If compound source/destination support mismatches, it either splits an unmapped source folio or cancels migration.
- It only allows migration to device private/coherent memory for anonymous memory; swap cache may be freed first with `folio_free_swap()`.
- It rejects unsupported ZONE_DEVICE destination types.
- It uses `folio_migrate_mapping()` and `folio_migrate_flags()` for the actual metadata move.

The driver remains responsible for allocating destination pages, copying contents, marking destination entries valid, and ensuring copy completion before finalization.

## Page Table Insertion

`migrate_vma_insert_page()` mirrors anonymous fault insertion logic for device or normal destination pages. It allocates page tables, prepares anon-vma, charges memcg, marks the folio uptodate, builds either a device-private swap PTE or normal PTE, handles zero-page replacement, checks stable address space and userfaultfd-missing state, adds anonymous rmap, optionally adds the folio to LRU, and installs the PTE.

When THP migration is enabled, `migrate_vma_insert_huge_pmd_page()` performs analogous PMD insertion, including memcg charge, pgtable deposit, huge PMD entry construction, rmap setup, zero PMD replacement, and THP fault accounting.

## Finalization

`__migrate_device_finalize()` walks all entries and chooses destination if migration succeeded, otherwise source. Non-device destinations are added back to LRU. It calls `remove_migration_ptes()` to restore CPU mappings and releases locks/references, preserving a supplied fault folio lock when required.

## Concurrency and Driver Contract

The API assumes the caller holds `mmap_lock` appropriately via the VMA context and that destination pages are locked. MMU notifier invalidation tells devices that CPU mappings are being migrated; `pgmap_owner` lets a driver avoid invalidating its own pages unnecessarily. Migration is best-effort except device-to-system fault recovery paths, where failure can propagate to severe userspace faults if the driver cannot bring device-private memory back.
