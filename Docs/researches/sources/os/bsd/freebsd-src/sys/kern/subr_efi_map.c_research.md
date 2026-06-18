# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_efi_map.c

## Purpose
Processes UEFI memory map descriptors for physical memory discovery, exclusion of runtime/reserved ranges, and diagnostic printing.

## Key Elements
- Iterator: `efi_map_foreach_entry()`.
- Physmem add pass: `efi_map_add_entries()`.
- Physmem exclusion pass: `efi_map_exclude_entries()`.
- Entry handler: `handle_efi_map_entry()`.
- Printer: `efi_map_print_entries()`.

## Behavior
`efi_map_foreach_entry()` computes the descriptor array offset after `struct efi_map_header`, validates descriptor size, and invokes a callback for every descriptor.

The memory map is handled in two passes. The add pass calls `physmem_hardware_region()` for usable loader, boot service, conventional, reclaim, runtime code, and runtime data ranges. The exclude pass removes ACPI reclaim, runtime code, and runtime data from allocation with `EXFLAG_NOALLOC`, while still allowing them to be represented in the direct map.

Printing decodes EFI memory type names, physical and virtual addresses, page counts, and memory attributes such as UC, WC, WB, XP, NV, RO, and RUNTIME.

## Research Notes
Runtime firmware memory is deliberately added first and excluded later so it can be mapped but not used for general allocation.
