# File Research: sources/os/linux/linux/mm/ptdump.c

## Purpose

`mm/ptdump.c` implements generic page-table dumping support around the `mm_walk` framework. It walks kernel page tables, reports entries to an architecture-provided `struct ptdump_state`, optimizes KASAN shadow walks, and exposes a debugfs `check_wx_pages` file for W+X mapping checks.

## Walk Callbacks

The file defines callbacks for each page-table level:

- `ptdump_pgd_entry()`
- `ptdump_p4d_entry()`
- `ptdump_pud_entry()`
- `ptdump_pmd_entry()`
- `ptdump_pte_entry()`
- `ptdump_hole()`

Each level reads the entry with the appropriate getter (`pgdp_get`, `p4dp_get`, `pudp_get`, `pmdp_get`, `ptep_get`). If the `ptdump_state` supplies an `effective_prot_*` callback, it is invoked before leaf handling. Leaf entries are reported through `note_page_*()` and the walk action is set to continue at the next range.

`ptdump_hole()` synthesizes zero entries for holes at the corresponding depth and reports them through the same note callbacks.

## KASAN Optimization

For generic or software-tag KASAN, large portions of the kernel address space may point to the early KASAN shadow page tables. The callback checks whether a page-table entry points at the KASAN early shadow table/page and calls `note_kasan_page_table()` directly, avoiding expensive descent through all lower-level KASAN shadow mappings.

## Public Walker

`ptdump_walk_pgd(st, mm, pgd)`:

- Takes `get_online_mems()`.
- Takes `mmap_write_lock(mm)`.
- Walks each configured `ptdump_range` through `walk_page_range_debug()`.
- Releases locks and flushes the final accumulated range through `st->note_page_flush(st)`.

The write mmap lock and memory hotplug guard stabilize the walk over kernel page tables and memory ranges.

## Debugfs W+X Check

`check_wx_show()` prints `SUCCESS` or `FAILED` based on `ptdump_check_wx()`. `ptdump_debugfs_init()` creates `check_wx_pages` as a read-only debugfs file at device initcall time.

## Filesystem/MM Relevance

This is diagnostic MM infrastructure. It helps validate kernel mapping permissions, especially W+X checks, and gives architecture code a generic page-table traversal engine for debugfs page-table dumps.
