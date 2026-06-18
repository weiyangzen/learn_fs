# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfile.c

## Purpose

Implements the online scrub `xfile` abstraction: a private, unlinked shmem-backed temporary file used as swappable indexed memory for scrub and repair staging data.

## Main Responsibilities

- Creates and destroys private shmem kernel files with `xfile_create` and `xfile_destroy`.
- Reads and writes arbitrary byte ranges directly through shmem folios:
  - `xfile_load`
  - `xfile_store`
- Provides sparse-data discovery through `xfile_seek_data`.
- Exposes locked folio access for objects that fit inside one folio:
  - `xfile_get_folio`
  - `xfile_put_folio`
- Discards cached backing pages through `xfile_discard`.
- Uses a private lockdep class for the shmem inode rwsem because these files are not exposed to userspace and access is coordinated by scrub callers.

## Important Invariants

- `xfile` treats short I/O and shmem allocation failure as `-ENOMEM`, because callers use it like memory.
- Callers are responsible for concurrency; normal VFS locking is intentionally bypassed.
- `xfile_get_folio` returns a locked folio only if the requested range fits fully inside that folio.
- `XFILE_ALLOC` can extend file size before folio allocation.
- Highmem pages are disallowed by setting the mapping GFP mask to `GFP_KERNEL`, so scrub code can directly use `folio_address`.

## Dependencies

- Depends on tmpfs/shmem via `shmem_kernel_file_setup`, `shmem_get_folio`, and `shmem_truncate_range`.
- Uses scrub tracing hooks from `scrub/trace.h`.
- Uses `memalloc_nofs_save` around folio allocation/copy loops to avoid filesystem reclaim recursion.

## Research Notes

This file is scrub’s private spill-to-shmem mechanism. It deliberately avoids user-visible file descriptors and relies on direct page-cache access rather than VFS read/write helpers.
