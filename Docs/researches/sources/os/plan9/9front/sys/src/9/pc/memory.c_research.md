# File Research: sources/os/plan9/9front/sys/src/9/pc/memory.c

## Purpose
Builds and finalizes the PC physical memory map, reserves BIOS/kernel regions, discovers RAM, maps low memory, and exposes allocation helpers for UPA/UMB device address spaces.

## Key Elements
Defines memory classes for unbacked physical address space, upper memory blocks, RAM, ACPI, and reserved ranges. `rampage()` allocates early page-table pages from `conf.mem` or directly from the memory map. `mapkzero()` maps RAM/UMB ranges into KZERO with correct caching flags. Low-memory helpers locate EBDA, conventional memory size, BIOS tables, VGA/ROM reservations, and UMB device ROMs. `checksum`, `sigscan`, `sigsearch`, and `rsdsearch()` find BIOS/ACPI signatures including RSDP. `upaalloc`, `upaallocwin`, `upafree`, `umballoc`, and `umbfree` allocate device address ranges. `umbexclude()` parses boot exclusions. `mtrrexclude()` removes ranges with unexpected cache attributes. `e820scan()` parses bootloader E820 data and maps usable RAM; `ramscan()` probes RAM when E820 is unavailable. `meminit0()` seeds default maps, reserves kernel/bootstrap areas, discovers memory, and applies MTRR filtering. `memreserve()` reserves page-rounded ranges before finalization. `meminit()` maps UMBs and transfers usable RAM into `conf.mem[]`.

## Dependencies
Uses `MemMin` set by `l.s`, memory-map APIs (`memmapadd`, `memmapalloc`, `memmapfree`, `memmapnext`, `memmapsize`), mapping APIs (`pmap`, `vmap`, `vunmap`, `punmap`), MTRR attributes, boot config, and `conf.mem`.

## Behavior/Risks
The bootloader E820 map is preferred; otherwise the kernel probes memory in 4 MB chunks and stops after high missing memory to avoid mistaking device/video regions for RAM. BIOS/UEFI maps may be unreliable, so `memreserve()` is intended for architecture code to protect discovered tables before final allocation.
