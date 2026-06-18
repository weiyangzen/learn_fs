# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_physmem.c

## Purpose
Maintains early physical memory region tables, exclusion regions, and derived availability lists for VM allocation, crash dumps, and RAM resource reservation.

## Main Interfaces
- `physmem_hardware_region()`: add usable physical RAM region.
- `physmem_exclude_region()`: add exclusion region with flags such as no-alloc/no-dump.
- `physmem_avail()`, `physmem_all()`: generate availability arrays.
- `physmem_excluded()`: query if a range is fully excluded.
- Kernel-only `physmem_init_kernel_globals()`: fills `phys_avail`, `dump_avail`, `physmem`, `realmem`, and `Maxmem`.
- Diagnostics: `physmem_print_tables()`, DDB `show physmem`.
- Kernel-only RAM pseudo-driver reserves memory resources.

## Implementation Notes
Two sorted static arrays track hardware and exclusion regions. `insert_region()` insertion-sorts and merges compatible overlapping/adjacent regions. Exact duplicate exclusions with different nonzero flags are upgraded by OR-ing flags.

`regions_to_avail()` walks hardware regions against sorted exclusions, page-aligns hardware bounds, splits around exclusions, merges adjacent output entries, optionally enforces a maximum physical memory byte cap from `hw.physmem`, and returns count plus page totals.

`physmem_hardware_region()` filters page zero because physical address zero conflicts with `pmap_extract()` failure semantics. It also avoids the top megabyte near the maximum physical address to prevent wrap/end-of-address-space problems.

The RAM pseudo-driver reserves non-excluded/non-dump physical ranges as bus memory resources.

## Dependencies
Uses VM page macros, `phys_avail`, `dump_avail`, bus resource APIs, nexus driver attachment, optional ACPI sizing, and DDB.

## Research Notes
This file directly shapes what memory the VM and dump subsystems see. Storage/filesystem behavior can be indirectly affected through dump availability and physical-memory sizing.
