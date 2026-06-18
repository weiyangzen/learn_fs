# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs.h

This is the internal NILFS kernel header. It defines debug categories/macros, inode hash sizing, mount/device/node forward declarations, malloc pools, and core in-memory structures for mounted NILFS devices and per-vnode NILFS nodes.

`struct nilfs_device` represents a backing device and shared filesystem state: device vnode, mount pointer, reference count, device/block sizes, primary and secondary superblocks, metadata file nodes for DAT/CP/SU, metadata layout descriptors, segment/checkpoint running state, last segment summary, super root, sync state, and lists of mounts. `struct nilfs_mount` represents a mounted head/checkpoint/snapshot view. `struct nilfs_node` embeds `genfs_node`, links to vnode/mount/device, stores inode contents, directory hash, node lock fields, file flags, lockf list, and hash-chain membership.

The header also defines NILFS node flag bits such as access/change/update/modify requests, modified/accessed markers, rename/delete state, sleep-lock state, sync state, callback unlock, and node rebuild.

Integration points: included by NILFS vnode, mount, allocation, translation, directory, and sync code. It ties NetBSD genfs/vnode infrastructure to NILFS on-disk structures from `nilfs_fs.h`.

Risks: comments explicitly warn that `node_mutex` should be held before reading/writing node state, and several fields/comments are marked `XXX`, suggesting incomplete or evolving locking/sync design. The in-memory structs are private but central; changes affect every NILFS kernel source file.
