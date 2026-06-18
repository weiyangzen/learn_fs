# File Research: sources/os/linux/linux-stable/fs/openpromfs/inode.c

## Scope

This file implements `openpromfs`, a single-instance pseudo filesystem exposing OpenPROM device-tree nodes as directories and properties as files.

## Public And Internal APIs Covered

- Inode private state: `struct op_inode_info` records whether an inode is a device node or property and stores the corresponding pointer.
- Property display: `is_string()`, `property_show()`, seq-file operations, `property_open()`, and `openpromfs_prop_ops`.
- Directory support: `openpromfs_lookup()`, `openpromfs_readdir()`, `openprom_operations`, `openprom_inode_operations`.
- Superblock and mount support: `openprom_alloc_inode()`, `openprom_free_inode()`, `openprom_iget()`, `openprom_fill_super()`, fs context operations, `openprom_fs_type`.
- Module lifecycle: slab cache creation/destruction and filesystem registration/unregistration.

## Control Flow And Behavior

- Lookup scans child OpenFirmware nodes first, then properties, matching dentry names to node basenames or property names under `op_mutex`.
- New node inodes become read/execute directories with lookup/readdir operations; property inodes become regular files using seq-file read operations.
- `security-password` under the `options` node is restricted to owner read/write while other properties are world-readable.
- Readdir emits `.` and `..`, then all child nodes as directories, then all properties as regular files, using OpenPROM unique IDs as inode numbers.
- Property reads render printable string lists separated by ` + `, otherwise render bytes or 32-bit words as hexadecimal text.
- `openprom_fill_super()` creates the root inode for `/`, sets `SB_NOATIME`, block size, magic, operations, and anonymous root dentry.

## State, Dependencies, And Invariants

- Protects OpenPROM traversal with global `op_mutex`.
- Depends on SPARC/OpenPROM interfaces: `struct device_node`, `struct property`, `of_find_node_by_path()`, `of_node_name_eq()`, and OpenPROM unique IDs.
- Root inode number is fixed at `OPENPROM_ROOT_INO`.
- Inode cache lifetime is protected with `rcu_barrier()` before slab destruction.
