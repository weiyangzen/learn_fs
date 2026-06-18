# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_map.c

## Purpose

Implements `/proc/<pid>/map`, a text representation of the target process VM map including address ranges, resident/private page counts, object metadata, protection bits, COW flags, backing type/path, and charged credential information.

## Main Entry Point

`procfs_doprocmap()`:
- requires `p_candebug()` and read-only access.
- rejects 32-bit callers reading a 64-bit target under `COMPAT_FREEBSD32`.
- obtains a referenced `vmspace`, locks the VM map for reading, and iterates non-submap entries.
- locks VM objects along backing chains to gather object type, vnode path, resident counts, flags, reference count, and shadow count.
- temporarily drops the VM map lock while formatting each entry and resolving vnode full paths.
- re-locks the map and uses the timestamp to recover if the map changed while unlocked.
- emits one line per mapping with start/end, residency, object pointer unless hidden for 32-bit wrapping, protection string, object counts/flags, COW/needs-copy state, type, path, charge marker, and charged uid.

## Integration Points

Registered by `procfs.c` as `map` with `PFS_RD` and `procfs_notsystem`. It uses VM internals, `vn_fullpath()`, `vmspace_acquire_ref()`, `kern_proc_vmmap_resident()`, and `vm_object_kvme_type()`.

## Risks and Review Notes

The function intentionally cannot provide an atomic full-map snapshot; it formats while dropping the map lock and compensates with map timestamps. Large maps can overflow the sbuf and terminate early, matching the file comment’s expectation that readers may need larger buffers.
