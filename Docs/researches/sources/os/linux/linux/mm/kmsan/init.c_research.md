# File Research: sources/os/linux/linux/mm/kmsan/init.c

## Role

Boot-time initialization for KMSAN metadata. It records early memory ranges requiring metadata, allocates metadata before normal allocation is fully available, and completes runtime startup.

## Future Metadata Ranges

- `kmsan_record_future_shadow_range()` records virtual ranges for later metadata allocation.
- Ranges are page-aligned and merged with overlapping existing entries.
- The static table holds up to `NUM_FUTURE_RANGES` entries and warns on overflow or invalid ranges.

## Early Shadow Initialization

`kmsan_init_shadow()` records and allocates metadata for:

- Reserved memblock ranges.
- Kernel `.data`.
- `NODE_DATA()` structures for each online node.

It calls `kmsan_init_alloc_meta_for_range()` for every merged recorded range.

## Memblock Page Recycling Scheme

- `kmsan_memblock_free_pages()` implements eager metadata allocation while memblock frees pages to the page allocator.
- For each order, the first freed block is held as shadow, the second as origin, and the third becomes the real page block receiving those metadata blocks.
- Metadata association is installed with `kmsan_setup_meta()`.
- This effectively uses two thirds of incoming early pages as metadata for the remaining third until normal setup completes.

## Leftover Metadata Recovery

- `held_back[]` stores unmatched shadow/origin blocks by page order.
- `smallstack` and `collect` provide a small temporary stack for splitting leftover higher-order blocks.
- `kmsan_memblock_discard()` walks orders high-to-low, collects leftovers, groups blocks in triples, assigns two as metadata for the third, frees usable pages, and splits remainders to lower order.

## Runtime Enable

- `kmsan_init_runtime()` initializes the `init_task` KMSAN context, discards/reclaims leftover memblock metadata blocks, logs startup warnings, and sets `kmsan_enabled = true`.

## Dependencies

Uses memblock, reserved memory iteration, node data, section symbols, page allocator core free path, and KMSAN shadow setup.

## Research Notes

This file solves the bootstrap problem that KMSAN needs shadow/origin memory before the ordinary allocator can safely run under KMSAN. The held-back triple scheme is central: two page blocks become metadata for the third, with leftovers split and recovered at the end.
