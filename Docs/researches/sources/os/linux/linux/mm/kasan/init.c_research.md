# File Research: sources/os/linux/linux/mm/kasan/init.c

KASAN shadow memory initialization and zero-shadow mapping management.

Key data:
- `kasan_early_shadow_page`: early read-only shadow backing page, later reused as zero shadow.
- Early page-table arrays for p4d/pud/pmd/pte levels depending on `CONFIG_PGTABLE_LEVELS`.

Initialization flow:
- `early_alloc()` allocates page-table memory from memblock before slab is ready.
- `kasan_populate_early_shadow()` populates a shadow range with mappings to the shared early shadow page, using large page-table coverage where alignment permits.
- `zero_pte/pmd/pud/p4d_populate()` build zero-shadow mappings and allocate lower-level tables either from slab or memblock.

Removal/addition:
- `kasan_remove_zero_shadow(start, size)` walks shadow page tables and clears entries that map the early shadow page, freeing now-empty page-table levels.
- `kasan_add_zero_shadow(start, size)` repopulates zero shadow for a memory range and rolls back on failure.

Invariants:
- Add/remove sizes must be aligned to `KASAN_MEMORY_PER_SHADOW_PAGE`.
- Removal validates that present PTEs point at the early shadow page before clearing.
- This code directly manipulates `init_mm` page tables and is therefore architecture/page-table-layout sensitive.
