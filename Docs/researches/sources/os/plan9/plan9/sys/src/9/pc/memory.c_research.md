# File Research: sources/os/plan9/plan9/sys/src/9/pc/memory.c

PC bootstrap memory discovery and physical address map management. The file owns early RAM/UMB/UPA maps, BIOS signature searches, E820 probing, fallback physical RAM probing, and the public allocators used by low-level device and kernel setup code.

Key elements:
- Defines `Map` and `RMap` free-list style maps for RAM, upper memory blocks, writable UMB device memory, and unbacked physical address space.
- `mapfree`, `mapalloc`, `mapprint` implement sorted range insertion, coalescing, and aligned/specific allocation.
- `rampage` allocates early page-table pages directly from `rmapram`, before normal kernel allocators are ready.
- `umbscan`, `umbexclude`, `umbmalloc`, `umbrwmalloc` manage 640K-1M device/ROM/window memory.
- `sigsearch` scans EBDA/base memory/BIOS ROM for firmware tables such as MP and ACPI signatures.
- `lowraminit` adds conventional memory and the gap between kernel end and `MemMin`.
- `e820scan` invokes BIOS INT 15h E820 through `realmode`, sorts entries, and maps low 32-bit memory.
- `ramscan` is the fallback CMOS/probe path, dynamically building page tables while testing memory 1MB at a time.
- `meminit` sets special VGA/BIOS cache attributes, scans memory, and fills `conf.mem`.
- `upaalloc`, `upafree`, `upareserve` provide physical address space allocation for device BAR-like needs.

Interactions:
- Calls MMU helpers `mmuwalk`, `pdbmap`, `mmuflushtlb`, and early `rampage` is called from `mmu.c`.
- Uses `realmode` for E820 and `getconf` flags such as `*maxmem`, `*norealmode`, `*noe820scan`, `umbexclude`.
- PCI code reserves discovered BAR memory through `upareserve`.

Research notes:
- This is core to Plan 9 PC memory topology, not filesystem logic directly, but it is required substrate for storage drivers and DMA-capable devices.
- Only maps memory usable through the 32-bit KZERO window; addresses above 4GB are ignored/truncated in E820 processing.
