# File Research: sources/os/linux/linux-stable/fs/ocfs2/ioctl.c

Purpose: implements OCFS2 ioctl dispatch, file attribute get/set support, filesystem information aggregation (`OCFS2_IOC_INFO`), online resize/group-add ioctls, reflink ioctl dispatch, FITRIM dispatch, extent movement dispatch, and compat ioctl handling.

Read coverage: complete file read, 1,003 lines.

Key structures and state:
- `ocfs2_info_request` is the common userspace request header used by all `OCFS2_IOC_INFO` subrequests.
- Information payloads handled here include block size, cluster size, max slots, label, UUID, feature bits, journal size, free-inode stats, and free-fragmentation stats.
- `OCFS2_INFO_FL_NON_COHERENT` controls whether info scans use cluster locks/system inodes or raw block reads.

Major logic:
- `ocfs2_fileattr_get()` takes a shared inode lock, refreshes OCFS2 inode flags from VFS flags, and exposes visible flags through `fileattr_fill_flags()`.
- `ocfs2_fileattr_set()` rejects fsxattrs, takes an exclusive inode lock, masks unsupported/modifiable flags, rechecks immutable/append capability under lock, journals an inode update, updates ctime and on-disk attributes, and commits.
- Simple info handlers copy request structs from userspace, fill scalar superblock/journal fields, mark requests filled, and copy results back.
- Free-inode info scans each slot's inode allocator. Coherent mode locks allocator inodes; non-coherent mode resolves system inode names and reads blocks directly.
- Free-fragmentation info scans global bitmap chain records and group descriptors, builds a power-of-two free-chunk histogram, tracks min/max/average free extents, and counts fully free chunks at the requested chunk size.
- Info request validation checks magic, exact request struct size, and request code; unknown valid requests are copied back with `FILLED` cleared for forward compatibility.
- `ocfs2_info_handle()` processes an array of request pointers, with compat pointer-array handling in `ocfs2_get_request_ptr()`.
- `ocfs2_ioctl()` dispatches space reservation, group extend/add, reflink, info, FITRIM, and move-extents commands with capability checks and mount write guards where required.
- `ocfs2_compat_ioctl()` handles compat reflink pointers and compat info request arrays, then delegates compatible commands to the native ioctl path.

Important entry points:
- `ocfs2_fileattr_get()`, `ocfs2_fileattr_set()`.
- `ocfs2_ioctl()`, `ocfs2_compat_ioctl()`.
- Internal info path: `ocfs2_info_handle()`, `ocfs2_info_handle_request()`, `ocfs2_info_handle_freeinode()`, `ocfs2_info_handle_freefrag()`.

Concurrency and lifetime:
- Attribute mutation is serialized by OCFS2 inode locking and a JBD2 transaction.
- Coherent info scans lock system inodes before reading allocator state; non-coherent scans intentionally trade freshness for avoiding cluster coordination.
- FITRIM and resize/group-add operations use VFS mount write protection.
- Freefrag bitmap scans hold global bitmap locking only in coherent mode and release all inode/buffer references on exit.

Important dependencies:
- Depends on OCFS2 inode locks, journaling, resize, reflink/refcount tree, directory/system-file lookup, suballocator/group descriptor readers, buffer-head I/O, trim, and move-extents code.
- Uses Linux `fileattr`, compat ioctl, capability, block discard, and userspace copy helpers.

Risk and edge cases:
- `OCFS2_IOC_INFO` pointer arrays require careful compat conversion; each request pointer can fault independently.
- Error reporting for info subrequests is best effort: `o2info_set_request_error()` may update only request flags in userspace.
- Non-coherent freefrag scans must clamp invalid `bg_bits` because raw reads bypass group descriptor validation.
- Freefrag chunk size must be nonzero and a power of two, and must not exceed clusters per group.
- Group extend/add and FITRIM require capabilities; move-extents performs its own write/regular-file/immutable checks in `move_extents.c`.
