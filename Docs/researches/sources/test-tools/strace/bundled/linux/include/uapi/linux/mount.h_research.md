# sources/test-tools/strace/bundled/linux/include/uapi/linux/mount.h

Purpose: defines mount-related userspace ABI constants and structures for legacy `mount(2)` flags and newer file-descriptor based mount APIs, mount attributes, `statmount(2)`, and `listmount(2)`.

Important APIs/types/functions: exports `MS_*`, `OPEN_TREE_*`, `MOVE_MOUNT_*`, `FSOPEN/FSPICK/FSMOUNT_*`, `enum fsconfig_command`, `MOUNT_ATTR_*`, `struct mount_attr`, `struct statmount`, `struct mnt_id_req`, `STATMOUNT_*`, `LSMT_ROOT`, `LISTMOUNT_REVERSE`, and `STATMOUNT_BY_FD`.

Control flow: tools open or clone mount trees, configure fs contexts with `fsconfig`, create mounts, move them, set attributes with `mount_setattr`, and query/list mount metadata using request masks.

State/persistence behavior: mount operations mutate namespace mount topology, propagation, idmapping, and superblock configuration. `statmount`/`listmount` are read-only snapshots returning versioned structs and trailing string storage.

Dependencies/integration: depends on Linux types and `O_CLOEXEC` from included build context. Integrates with VFS, namespaces, idmapped mounts, filesystem drivers, and `/proc/*/mountinfo` replacement APIs.

Risks and test signals: versioned struct sizes, string offsets, mask negotiation, and flag aliasing (`MS_VERBOSE`/`MS_SILENT`) are subtle. Tests should cover every syscall flag family, `mount_attr` bit sets/clears, `statmount` string buffers, and list iteration.
