# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_node.h

This header defines HSFS in-core node, volume, mount, fid, and I/O scheduling state.

Directory entry abstraction:
- `hs_direntry` normalizes on-disk directory data into extent location/size, timestamps, vnode type, mode, link count, owner/group, inode, device number, XAR metadata, interleave fields, and symlink data.

Path table structures:
- `ptable` stores path-table entry name data.
- `ptable_idx` links a directory’s path-table entry to its parent and child range.

Node model:
- `hsnode` is the in-core file node, with hash/free list links, vnode pointer, cached directory entry, node id, directory entry disk location, path-table index, directory search offset, page mapping count, sequence, flags, read-ahead state, and contents lock.
- Node ids use the starting extent for directories and usually files, with `HS_DUMMY_INO` used for empty files.

Volume and mount:
- `hs_volume` is immutable after initialization and contains volume size, logical-block size/shift data, file structure version, default uid/gid/protection, creation/modification times, root dir entry, path table location/length, volume set data, and volume id.
- `hsfs` contains mount-list linkage, magic, VFS/root/device vnodes, volume type, parsed volume, path tables, extension flags, SUA offset, name-length limits, error flags, mount name/options, hsnode hash/free lists, kstat counters, and I/O scheduling queue.

I/O scheduling:
- `hio` represents a read request in AVL trees ordered by offset and deadline.
- `hio_info` tracks read-ahead request buffers, virtual addresses, semaphores, pages, and filesystem pointer.
- `hsfs_queue` stores circular-look scheduling state, preallocated coalescing buffer, locks, offset/deadline AVL trees, read-ahead taskq, max read-ahead, and device max transfer.

Constants/macros:
- Volume types include High Sierra, ISO, ISO v2, and Joliet.
- Error bit offsets track nonconformant media cases such as lower-case names, bad root dir, unsupported type, bad file lengths, and bad SUA length.
- Conversion macros map VFS/vnode to HSFS/hsnode and convert logical blocks, sectors, and byte offsets.

Dependencies and relationships:
- This is the central in-core state header for HSFS.
- Paired with `hsfs_spec.h`, `hsfs_isospec.h`, `hsfs_susp.h`, and `hsfs_rrip.h` for on-disk parsing and extensions.
