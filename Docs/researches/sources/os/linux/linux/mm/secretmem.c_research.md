# File Research: sources/os/linux/linux/mm/secretmem.c

## Purpose

`mm/secretmem.c` implements `memfd_secret(2)`, creating anonymous file descriptors whose mappings allocate pages removed from the kernel direct map. The goal is to reduce exposure of sensitive userspace memory through direct-map aliases and core dumps.

## Enablement and Global State

- `secretmem_enable` is a read-only-after-init module parameter named `secretmem.enable`.
- `secretmem_users` counts active secretmem files.
- `secretmem_active()` reports whether any users exist.
- Initialization is skipped if secretmem is disabled or the architecture cannot change the direct map (`can_set_direct_map()`).

## Fault Path

`secretmem_fault()` handles page faults on secretmem VMAs:

1. Rejects offsets beyond inode size.
2. Takes `filemap_invalidate_lock_shared(mapping)`.
3. Attempts to lock an existing folio at the fault offset.
4. If absent, allocates a zeroed order-0 folio.
5. Calls `set_direct_map_invalid_noflush()` on the page before inserting it.
6. Marks the folio uptodate and inserts it into the file mapping.
7. On insertion races, restores direct-map default state and retries for `-EEXIST`.
8. Flushes the kernel TLB range covering the page after insertion.
9. Returns the locked file page to the fault handler.

The direct-map invalidation happens before the page becomes visible through the page cache, and error paths restore the direct map when insertion fails.

## VMA Setup

`secretmem_mmap_prepare()` requires shared mapping permissions (`VMA_SHARED_BIT` or `VMA_MAYSHARE_BIT`), sets `VM_LOCKED` and `VM_DONTDUMP`, verifies `mlock_future_ok()`, and installs `secretmem_vm_ops`. `vma_is_secretmem()` recognizes secretmem VMAs by comparing `vm_ops`.

The locked flag keeps pages resident; `VM_DONTDUMP` excludes them from core dumps.

## File, Inode, and Address-Space Operations

`secretmem_file_create()` creates a secure anonymous inode on the internal secretmem pseudo mount, allocates a pseudo file, configures the mapping as `GFP_HIGHUSER` and unevictable, installs inode and address-space operations, marks the inode as regular, initializes size to zero, and increments `secretmem_users`.

`secretmem_release()` decrements `secretmem_users`.

`secretmem_aops`:

- Uses `noop_dirty_folio`.
- Refuses migration via `secretmem_migrate_folio()` returning `-EBUSY`.
- Restores the direct map and zeros memory in `secretmem_free_folio()`.

`secretmem_setattr()` permits setting size only while the inode size is still zero; later resize attempts with `ATTR_SIZE` fail with `-EINVAL`. It serializes against faults with `filemap_invalidate_lock()`.

## Syscall and Pseudo Filesystem

`SYSCALL_DEFINE1(memfd_secret, flags)`:

- Verifies local flags do not overlap `O_CLOEXEC`.
- Returns `-ENOSYS` if disabled or unsupported by direct-map controls.
- Rejects unknown flags.
- Creates the secretmem file and installs it into an fd, honoring `O_CLOEXEC`.

The pseudo filesystem is named `secretmem`, uses `SECRETMEM_MAGIC`, and is mounted internally during `fs_initcall(secretmem_init)`.

## Security and Invariants

- Pages are removed from the direct map before insertion into the mapping.
- Pages are restored to the direct map and zeroed on free.
- Mappings are shared, locked, unevictable, nondumpable, and non-migratable.
- Architecture support for direct-map modification is mandatory.
- The backing file begins at size zero and can only be sized once.

## Filesystem/MM Relevance

`secretmem.c` is implemented as a pseudo filesystem plus file-backed mapping. It exercises VFS file/inode/address-space operations while enforcing MM-specific secrecy properties: direct-map removal, locked unevictable pages, no migration, no core dump, and controlled fault-time allocation.
