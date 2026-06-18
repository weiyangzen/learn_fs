# File Research: sources/os/bsd/freebsd-src/sys/fs/fdescfs/fdesc_vnops.c

## Purpose
Implements vnode operations and vnode cache management for `fdescfs` descriptor entries.

## Main Elements
- Initializes/destroys a small hash table and `fdesc_hashmtx`.
- `fdesc_allocvp()` finds or creates synthetic vnodes keyed by descriptor index and mount, handling races, forced unmount, symlink/readlink flags, and `insmntque1()`.
- `fdesc_lookup()` resolves `.` and numeric descriptor names, rejects DELETE/RENAME, validates numeric syntax, obtains the target file without rights, and uses `vn_vget_ino_gen()` to avoid root vnode deadlocks.
- `fdesc_get_ino_alloc()` either returns the underlying vnode directly for `nodup` vnode descriptors or allocates a synthetic descriptor vnode.
- `fdesc_open()` returns `ENODEV` after setting `td_dupfd`, allowing upper open logic to duplicate the requested descriptor.
- `fdesc_pathconf()` reports root constants directly and delegates non-root queries to `kern_fpathconf()`.
- `fdesc_getattr()` fabricates stable attributes for root and descriptor entries.
- `fdesc_setattr()` delegates attribute changes to the underlying vnode when possible, with special handling for non-vnode descriptors and O_PATH descriptors.
- `fdesc_readdir()` emits `.`, `..`, and open descriptor numbers from the calling process descriptor table.
- `fdesc_readlink()` returns the full path for vnode-backed descriptors or an anonymous placeholder for other descriptor types.
- `fdesc_reclaim()` removes nodes from the hash and frees private data.

## Dependencies And Integration
Uses Capsicum no-rights checks, filedesc locking, vnode lifecycle APIs, process descriptor tables, and mount flags from `fdesc.h`.

## Risk Notes
Descriptor lookup is inherently process-relative. Lock ordering around root and underlying vnodes is carefully handled to avoid deadlocks when descriptors point back into fdescfs.
