# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vtoc.h

## Role

`vtoc.h` defines the illumos VTOC partition-table ABI, extended VTOC layout, compatibility conversion macros, partition tags/flags, error codes, and read/write routines.

## Key Interfaces

The file defines:
- `V_NUMPAR` from `NDKMAP`.
- sanity/version constants `VTOC_SANE`, `V_VERSION`, and `V_EXTVERSION`.
- partition tags for root, swap, usr, backup, EFI/GPT system/reserved, VxVM, BIOS boot, NetBSD FFS, FreeBSD partition types, and unknown.
- permission flags `V_UNMNT` and `V_RONLY`.
- VTOC operation error returns such as `VT_ERROR`, `VT_EIO`, `VT_EINVAL`, `VT_ENOTSUP`, `VT_ENOSPC`, and `VT_EOVERFLOW`.

Structures:
- `struct partition` uses `daddr_t` and `long` sector counts.
- `struct vtoc` is the classic layout with boot info, sanity, version, volume name, sector size, partition count, reserved words, partition array, timestamps, and ASCII label.
- `struct extpartition` and `struct extvtoc` use 64-bit disk addresses/sizes.

## Compatibility

Kernel macros convert between `vtoc` and `extvtoc`. Under `_SYSCALL32`, the file defines `partition32`, `vtoc32`, and conversion macros between 32-bit, native, and extended layouts, including timestamp clamping to `TIME32_MAX`.

## Functions

The public routines are:
- `read_vtoc()`
- `write_vtoc()`
- `read_extvtoc()`
- `write_extvtoc()`

## Research Notes

The comments explain that Sun/illumos VTOC is not a literal AT&T second-sector VTOC; several fields are synthesized from disk labels and unsupported fields are returned as zero. Conversion macros cast sizes and starts, so overflow handling belongs in callers or the routines that use these macros.
