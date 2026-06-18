# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_shm.c

## Purpose
Implements POSIX shared memory objects for FreeBSD, backed by VM objects and exposed as file descriptors. It supports `shm_open2()`, legacy `shm_open()`, unlink, rename/exchange, anonymous objects, largepage objects, sealing, file-like read/write/truncate/fallocate/fspacectl operations, mmap integration, and kernel mappings.

## Main Elements
- `struct shm_mapping`: named-object dictionary entries mapping full jail-rooted paths and FNV hashes to referenced `struct shmfd` objects.
- `shm_ops`: file operation table for shared memory descriptors, including read/write, truncate, ioctl, stat, close, chmod/chown, seek, mmap, seals, fallocate, space deallocation, sendfile, kinfo, comparison, and descriptor passing.
- VM I/O: `uiomove_object_page()` and `uiomove_object()` move data between uio and VM object pages; sparse reads can return `zero_region` without instantiating pages.
- Pager hooks: custom swap pager callbacks track resident/swap-backed page accounting in `shm_pages`; physical pager callbacks implement largepage populate/haspage/destructor behavior and largepage counters.
- Truncation: `shm_dotruncate_locked()`, `shm_dotruncate_largepage()`, `shm_dotruncate_cookie()`, and `shm_dotruncate()` enforce grow/shrink seals, kernel mapping constraints, swap reservation, page invalidation, and largepage alignment/allocation policy.
- Object lifecycle: `shm_alloc()`, `shm_hold()`, `shm_drop()`, and `shm_access()` allocate swap or physical pager objects, initialize timestamps/rangelocks/MAC labels, assign synthetic inode numbers, and release VM backing on last reference.
- Namespace operations: `shm_lookup()`, `shm_insert()`, `shm_remove()`, `shm_doremove()`, `shm_remove_prison()`, and `shm_get_path()` manage names, jail cleanup, and object path introspection.
- Open/unlink/rename: `kern_shm_open2()` handles flags, anonymous objects, supplied in-kernel shmfds, `O_CREAT`/`O_EXCL`/`O_TRUNC`, initial sealing policy, largepage selection, Capsicum rejection for named opens in capability mode, and descriptor creation. `sys_shm_rename()` implements no-replace and exchange semantics.
- Mapping paths: `shm_mmap()` computes max protections, write-count handling for writable shared mappings, atime updates, MAC checks, and normal or largepage mapping. `shm_mmap_large()` performs alignment, address selection, MAP_FIXED/MAP_EXCL handling, and direct VM map insertion for physical largepage objects.
- File-like helpers: `shm_read()`, `shm_write()`, `shm_seek()`, `shm_ioctl()`, `shm_stat()`, `shm_chmod()`, `shm_chown()`, `shm_fallocate()`, `shm_fspacectl()`, and `shm_deallocate()`.
- Seals and observability: `shm_add_seals()`, `shm_get_seals()`, `shm_fill_kinfo()`, `sysctl_posix_shm_list`, and `kern_shm_open()`/`sys_shm_open2()` wrappers.

## Dependencies And Integration
Connects file descriptors, Capsicum, audit, jail path rewriting, MAC hooks, VM pager/object/page APIs, swap reservation and per-credential accounting, rangelocks, resource limits, kernel maps, sysctls, `kinfo_file`, FNV hash dictionaries, and largepage/physical memory allocation. `vm_mmap.c` supplies complementary mapping behavior referenced by the file header.

## Risk Notes
This file is a concurrency and VM boundary. Rangelocks serialize read/write/truncate/fallocate/seal-sensitive ranges, while VM object locks protect backing pages and pager metadata. Write seals must reject future writable mappings and fail if existing writable mappings remain. Largepage shm objects are intentionally more restrictive: they require configured page size, aligned sizes/offsets, no private mappings, and currently do not support shrink/free of unmanaged pages. Rename temporarily holds objects while removing and reinserting names to preserve references across rollback and exchange cases.
