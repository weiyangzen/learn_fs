# File Research: sources/os/bsd/freebsd-src/sys/sys/efi_map.h

## Purpose
Declares kernel helpers for iterating and applying EFI memory map metadata.

## Main Elements
- `efi_map_entry_cb` callback type for `struct efi_md` entries.
- `efi_map_foreach_entry()` iterates entries in an EFI map header.
- `efi_map_add_entries()` and `efi_map_exclude_entries()` apply map entries to kernel memory management.
- `efi_map_print_entries()` prints entries.

## Dependencies And Integration
Kernel-only; includes `sys/efi.h` and `machine/metadata.h`.

## Risk Notes
EFI memory map interpretation affects physical memory availability and exclusions. Misclassification can reserve usable memory or use firmware-reserved memory unsafely.
