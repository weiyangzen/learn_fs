# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fbio.c

## Purpose

`fbio.c` implements pseudo-buffer-I/O routines backed by `segmap` mappings. It gives filesystem/kernel code an `fbuf` abstraction for accessing file data through locked kernel virtual addresses, then releasing or writing those mappings through `segmap_release()`.

## Main Operations

- `fbread()` maps a `MAXBSIZE`-aligned file window with `segmap_getmapflt()`, validates that `off + len` stays within a `MAXBSIZE` boundary, soft-locks the pages with `segmap_fault(F_SOFTLOCK)`, allocates an `fbuf`, and returns `fb_addr` pointing at the requested byte offset.
- `fbzero()` maps or creates pages for a file range, allocates an `fbuf`, calls `segmap_pagecreate()`, and zeroes the requested page-rounded memory region.
- `fbrelse()` releases a read or other mapping without forcing writeback.
- `fbwrite()` releases with `SM_WRITE` for direct writeback.
- `fbdwrite()` releases without `SM_WRITE`, corresponding to delayed-write style behavior.
- `fbiwrite()` writes an fbuf synchronously to an indirect block/device vnode through a temporary `buf` from `pageio_setup()` and `bdev_strategy()`.

## Shared Release Logic

The `FBCOMMON` macro computes the page-rounded region containing the fbuf, soft-unlocks it with `segmap_fault(F_SOFTUNLOCK)`, frees the `fbuf`, and releases the base segmap mapping with the caller-supplied flags. It is used for normal release, direct write, delayed write, and the cleanup half of indirect write.

## VM/VFS Interaction

The file depends on:

- `segkmap` and `segmap_getmapflt()`/`segmap_getmap()`.
- `segmap_fault()` for soft-lock and soft-unlock.
- `segmap_pagecreate()` for zero-fill/create behavior.
- `segmap_release()` for final mapping release and writeback policy.
- `pageio_setup()`, `bdev_strategy()`, `biowait()`, and `pageio_done()` for synchronous device write in `fbiwrite()`.

## Constraints and Edge Cases

Both `fbread()` and `fbzero()` panic if the requested range crosses a `MAXBSIZE` boundary. `fbzero()` contains an explicit warning that it will not work correctly when filesystem block size is smaller than `PAGESIZE`. `fbread()` converts object fault errors to the underlying errno when `FC_CODE(err) == FC_OBJERR`, otherwise returning `EIO`.

## Research Notes

This is a small but sensitive bridge between filesystem logical byte ranges and VM-backed kernel mappings. Correctness depends on strict `MAXBSIZE` windowing, balanced softlock/softunlock, and the caller choosing the right release/writeback variant.
