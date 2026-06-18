# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_extattr.c

Read completely: 1584 lines.

Implements ULFS/LFS extended attributes using ordinary backing files rather than changing the inode/on-disk file format. Attribute storage lives under `.attribute/system/<name>` or `.attribute/user/<name>` below the mounted filesystem root, and each backing file contains a file header followed by fixed-size per-inode attribute slots indexed by inode number.

Core behavior:
- `ulfs_extattr_uepm_init()` and `ulfs_extattr_uepm_destroy()` manage the per-mount EA state, list, credential, flags, and mutex.
- `ulfs_extattr_start()`, `ulfs_extattr_stop()`, and `ulfs_extattrctl()` implement mount-level EA lifecycle and privileged control operations.
- `ulfs_extattr_autostart()` discovers `.attribute/system` and `.attribute/user`, iterates each directory, opens regular backing files, and enables each attribute.
- `ulfs_extattr_autocreate_attr()` creates a backing file on first set when an attribute is missing, using `O_CREAT|O_EXCL`, writing a `ulfs_extattr_fileheader`, then enabling the new attribute.
- `ulfs_getextattr()`, `ulfs_listextattr()`, `ulfs_setextattr()`, and `ulfs_deleteextattr()` are vnode operation front ends that acquire the per-mount EA lock and call the internal get/list/set/remove helpers.

Data layout:
- Backing files begin with `struct ulfs_extattr_fileheader` containing magic, version, and maximum value size.
- Each inode has a slot at `sizeof(fileheader) + ino * (sizeof(attr_header) + uef_size)`.
- Each slot has `struct ulfs_extattr_header` with in-use flag, stored length, and inode generation.
- Headers are byte-swapped with `ulfs_rw32()` when the backing file magic indicates opposite endianness.

Lookup and locking:
- Active attributes are tracked by `struct ulfs_extattr_list_entry` on `ump->um_extattr.uepm_list`.
- The per-mount lock is a mutex plus manual recursion counter because vnode inactive/close paths can re-enter EA code while the lock is held.
- Backing vnodes are locked shared for reads/lists and exclusive for writes/removals unless the backing vnode is the same as the target vnode.

Access and semantics:
- Name validation rejects null and empty names.
- `extattr_check_cred()` performs per-attribute read/write authorization.
- Reads require offset zero and restore the caller `uio_offset` to zero after use.
- Writes replace the full value, reject nonzero offsets, and reject values larger than the backing file's configured maximum.
- Lists support both NUL-terminated names and `EXTATTR_LIST_LENPREFIX`.

Risks and notes:
- The file explicitly notes that data writes are not atomic with respect to header writes.
- One per-mount lock serializes all EA operations and is called out as overly coarse.
- `ulfs_extattr_iterate_directory()` allocates `dirbuf` but returns early on `ulfs_readdir()` error without freeing it.
- `ulfs_extattr_list()` calls `ulfs_extattr_get_header()` before locking each backing vnode, despite that helper's caller-locking comment.
- `ulfs_extattr_rm()` always unlocks `attribute->uele_backing_vnode` on exit, even though the surrounding comment says same-vnode cases may already be locked by the caller.
- Generation mismatches are treated as `ENODATA`, leaving stale slots for future cleanup.
