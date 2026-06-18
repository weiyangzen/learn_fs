# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_extattr.h

Read completely: 129 lines.

Defines the ULFS extended-attribute backing-file format, per-mount in-memory structures, and kernel prototypes used by `ulfs_extattr.c`.

Key definitions:
- `ULFS_EXTATTR_MAGIC`, `ULFS_EXTATTR_VERSION`, `.attribute`, `system`, and `user` define the backing-file discovery and validation contract.
- `ULFS_EXTATTR_MAXEXTATTRNAME` fixes attribute names at 256 bytes including NUL.
- `ULFS_EXTATTR_ATTR_FLAG_INUSE` marks a per-inode slot as active.
- `ULFS_EXTATTR_UEPM_INITIALIZED` and `ULFS_EXTATTR_UEPM_STARTED` mark per-mount EA lifecycle state.
- `ULFS_EXTATTR_CMD_START`, `STOP`, `ENABLE`, and `DISABLE` are the mount control operations.

Structures:
- `struct ulfs_extattr_fileheader` is the backing file header: magic, version, and per-inode value capacity.
- `struct ulfs_extattr_header` is the per-inode record header: flags, value length, and inode generation.
- `struct ulfs_extattr_list_entry` represents an enabled attribute, including its header, namespace, name, backing vnode, and byte-swap flag.
- `struct ulfs_extattr_per_mount` stores the mount-level mutex, enabled-attribute list, control credential, recursion counter, and flags.

Integration:
- Exposes per-mount init/destroy/start/autostart/stop, `ulfs_extattrctl()`, vnode EA operations, inactive cleanup, and module init/done hooks.

Risks and notes:
- The declared permission constants are not enforced in this header; actual checks happen through VFS/extattr authorization.
- Backing file compatibility depends on the fixed file/header layout and byte-swap flag handling in the implementation.
