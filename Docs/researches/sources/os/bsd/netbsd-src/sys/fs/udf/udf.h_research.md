# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf.h

Read completely: 432 lines.

This is the kernel-private UDF filesystem state header. It declares debug categories and `DPRINTF` macros, VFS prototypes, implementation identity strings, configuration limits, translation sentinels, buffer content hints, virtual-to-physical mapping types, allocation strategy ids, logical-volume open/close action bits, error-handling bits, and readdir cookie constants.

It defines UDF runtime structures: logical volume integrity trace entries, bitmaps, strategy argument and strategy operation tables, `struct udf_mount` for mounted volume state, and `struct udf_node` for vnode-backed files/directories. The mount structure tracks descriptors, fileset/root state, partition mapping, allocation strategy, sequential/VAT/sparable/metadata partition state, node rb-tree, sync state, and late allocation buffers. Nodes embed `genfs_node`, hold descriptor pointers, extent descriptors, dirhash, lock state, outstanding I/O counts, and related extended-attribute/stream nodes.

Important interactions: includes `ecma167-udf.h`, `udf_osta.h`, device/MMC headers, buffer queues, disk/kthread/malloc support, and genfs node support. The strategy table abstracts bootstrap, sequential, direct, and read-modify-write disc handling.

Security/reliability notes: most fields describe mutable mount-wide filesystem state. Correct locking is central: the file documents that `udf_node.node_mutex` must be claimed before reading/writing node state, and mount allocation/sync paths have their own mutexes.
