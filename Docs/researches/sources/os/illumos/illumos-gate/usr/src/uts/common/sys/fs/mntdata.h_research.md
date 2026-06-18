# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/mntdata.h

This header defines mntfs node, snapshot, and element structures used to expose mount table data.

Mount elements:
- `mntelem_t` stores list links, birth/death/vfs ctime, reference count, hidden flag, text buffer/size, and parsed `extmnttab` payload.
- Macros test whether an element is alive or dead based on death timestamp.

Snapshots:
- `mntsnap_t` stores snapshot time, last mount-table mtime, first/next element pointers, flags, element count, text size, and read offsets.
- Flags include show-hidden and rewind/refresh requirements.

Node state:
- `mntnode_t` stores vnode, mounted-on vnode, rwlock, node flags, and two snapshots: one for read and one for ioctl.

Filesystem state:
- Kernel `mntdata_t` stores zone reference, open count, cached normal/hidden snapshot sizes and mtimes, and embedded mntnode.

Conversions:
- `VTOM`, `MTOV`, and `MTOD` map between vnode, mntnode, and mount filesystem data.

Kernel API:
- Exposes `mntvnodeops`.
- `mntfs_getmntopts()` formats mount options for a VFS.

Dependencies and relationships:
- Used by mntfs to present `/etc/mnttab`-style data as a filesystem view.
- Supports hidden mounts via `MS_NOMNTTAB`-related snapshot handling.
