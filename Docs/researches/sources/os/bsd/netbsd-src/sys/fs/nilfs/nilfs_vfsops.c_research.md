# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_vfsops.c

Implements the NetBSD VFS layer for NILFS: module registration, mount/unmount, root vnode lookup, stat, vnode loading, and filesystem initialization.

Key points:
- Defines the `nilfs_vfsops` table for `MOUNT_NILFS` and module attach/detach.
- Initializes malloc types, global mounted-device list, and `nilfs_node_pool`.
- Provides genfs callbacks, including mark-update flag propagation; allocation is a no-op placeholder.
- Mount flow:
  - Validates mount args and locates the block device.
  - Opens the device and reads both NILFS superblocks.
  - Validates superblock CRCs and selects the newer valid spare if needed.
  - Calculates block size and metadata constants for DAT and ifile.
  - Searches for a valid super root and creates DAT, CPFILE, and SUFILE system nodes.
  - Selects a checkpoint, validates it, and builds the ifile node used by the mount.
- Supports multiple read-only checkpoint mounts from one device and prevents duplicate checkpoint mounts; read-write mounting is constrained but real writing is not implemented.
- `nilfs_loadvnode()` resolves inode records from the checkpoint ifile, creates a `nilfs_node`, sets vnode type/op table, initializes genfs, marks root, and sets UVM size.
- `nilfs_vget()`, file-handle conversion, root-mount, and snapshot operations are unsupported or return `EOPNOTSUPP`.

Risk/notes:
- Mounting is functional for read-only checkpoint access.
- The code contains several TODOs around write sessions, superblock writeout, roll-forward, and NFS/file-handle support.
