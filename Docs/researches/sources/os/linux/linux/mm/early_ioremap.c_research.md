# File Research: sources/os/linux/linux/mm/early_ioremap.c

## Purpose

Provides generic early boot temporary mapping helpers for architectures that need `early_ioremap()` / `early_memremap()` before normal `ioremap()` is available. The implementation is active for `CONFIG_MMU`; the non-MMU fallback returns direct physical-address casts.

## MMU Implementation

The file manages a fixed number of boot-time mapping slots using the fixmap area:

- `prev_map[FIX_BTMAPS_SLOTS]`: currently active mappings.
- `prev_size[FIX_BTMAPS_SLOTS]`: original requested sizes for unmap validation.
- `slot_virt[FIX_BTMAPS_SLOTS]`: virtual base for each fixmap slot.

`early_ioremap_setup()` initializes slot virtual addresses and warns if stale mappings exist.

## Main Mapping Flow

`__early_ioremap()`:

1. Finds a free slot.
2. Rejects zero size or address wraparound.
3. Saves original size.
4. Aligns physical address down and expands size to page boundaries.
5. Rejects requests requiring more than `NR_FIX_BTMAPS` pages.
6. Installs fixmap PTEs using `__early_set_fixmap()` before paging init reset, or `__late_set_fixmap()` after.
7. Stores and returns the virtual address plus original page offset.

`early_iounmap()`:

1. Finds the slot by returned address.
2. Verifies the supplied size matches the original request.
3. Computes aligned page count.
4. Clears fixmap entries with `__early_set_fixmap(..., FIXMAP_PAGE_CLEAR)` or `__late_clear_fixmap()`.
5. Marks the slot free.

## Public Helpers

- `early_ioremap()` maps I/O memory with `FIXMAP_PAGE_IO`.
- `early_memremap()` maps memory with `FIXMAP_PAGE_NORMAL`, after optional architecture adjustment.
- `early_memremap_ro()` maps read-only memory when `FIXMAP_PAGE_RO` exists.
- `early_memremap_prot()` maps with an explicit architecture pgprot value under `CONFIG_ARCH_USE_MEMREMAP_PROT`.
- `early_memunmap()` delegates to `early_iounmap()`.
- `copy_from_early_mem()` copies from physical memory in chunks that fit the early mapping slot capacity.

## Debug and Leak Detection

- Boot parameter `early_ioremap_debug` enables warnings with stack dumps for map/unmap activity.
- `check_early_ioremap_leak()` runs at `late_initcall` and warns if any slots remain mapped.

## Architecture Hooks

- Weak `early_memremap_pgprot_adjust()` lets architectures modify protections.
- Architectures may provide `__late_set_fixmap` / `__late_clear_fixmap`; otherwise default stubs `BUG()` after `early_ioremap_reset()` marks `after_paging_init`.

## Non-MMU Behavior

When `CONFIG_MMU` is disabled:

- `early_ioremap()` returns the physical address cast to `void __iomem *`.
- `early_memremap()` and `early_memremap_ro()` return direct `void *`.
- `early_iounmap()` is a no-op.
