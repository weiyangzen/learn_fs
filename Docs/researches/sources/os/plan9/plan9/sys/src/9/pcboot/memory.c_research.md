# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/memory.c

## Purpose
Bootstrap physical/virtual memory map management, initial page-table extension, UMB scanning, and allocation helpers.

## Main Interfaces
- Exports `mapprint`, `memdebug`, `mapfree`, `mapalloc`, `rampage`, `meminit`, `umbmalloc`, `umbfree`, `umbrwmalloc`, `umbrwfree`, `upaalloc`, `upafree`, `upareserve`, `memorysummary`, and `mapping`.

## Implementation Notes
- Maintains resource maps for unbacked physical address space, RAM, upper memory blocks, and read/write UMB device memory.
- `mapfree` inserts/coalesces ranges; `mapalloc` allocates by optional address and alignment.
- `rampage` allocates a page directly from RAM for page-table construction.
- `umbscan` scans `0xD0000-0xF0000` for ROM signatures, writable device memory, and floating-bus free UMB space, then applies `umbexclude`.
- `lowraminit` reserves already-used low memory, frees RAM above `Mallocbase`, and frees unbacked address space above `MemMax`.
- `map` updates resource maps and creates kernel virtual mappings for RAM/UMB regions.
- `meminit` double-maps low memory, sets VGA write-through and BIOS uncached attributes, scans UMBs, initializes low RAM maps, and fills `conf.mem`.

## Dependencies And Risks
- Designed for bootstrap needs, not full physical memory discovery; `MemMax` bounds mapping.
- Fixed-size map arrays can lose ranges and print warnings.
- UMB probing writes test bytes into candidate memory and must avoid ROM/device side effects.
