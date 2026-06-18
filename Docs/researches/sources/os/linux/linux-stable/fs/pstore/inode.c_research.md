# File Research: sources/os/linux/linux-stable/fs/pstore/inode.c

## Summary
Implements the `pstore` filesystem exposed at `/sys/fs/pstore`. It presents backend records as read-only regular files, supports unlink-to-erase, parses mount options, and coordinates record population/removal as backends register and unregister.

## Main Responsibilities
- Maintain the mounted pstore superblock and in-memory list of visible records.
- Create one file per `struct pstore_record`.
- Read ordinary records with `simple_read_from_buffer()` and ftrace records through seq_file decoding.
- Erase backend records on unlink when the backend supports `erase`.
- Parse and show the `kmsg_bytes` mount option.
- Register/unregister the `pstore` filesystem and sysfs mount point.

## Key Interfaces
- `pstore_mkfile()` creates a persistent dentry/inode for one backend record.
- `pstore_get_records()` asks the current backend to repopulate files.
- `pstore_put_backend_records()` removes all visible files for a backend.
- `pstore_init_fs()` and `pstore_exit_fs()` manage filesystem registration.
- `pstore_file_operations` handles open/read/llseek/release for record files.
- `pstore_dir_inode_operations` provides lookup and unlink.

## Important Behavior
Files are named `<type>-<backend>-<id>` with `.enc.z` appended for compressed records before decompression state is cleared. `pstore_mkfile()` de-duplicates by record type, id, and backend pointer to avoid duplicate files during rescans.

The filesystem is single-superblock. `psinfo_lock_root()` only returns a root dentry when both a backend and mounted superblock exist, and locks the root inode so file creation/removal is serialized with directory mutation.

Unlink first removes the record from the in-memory list, clears the dentry backpointer, then invokes the backend `erase()` under the backend read mutex. If no erase method exists, unlink fails with `-EPERM`.

## State and Synchronization
`records_list_lock` protects the global `records_list`. `pstore_sb_lock` protects `pstore_sb`. Backend read/erase operations use `record->psi->read_mutex`.

## Cross-File Interactions
`platform.c` calls `pstore_get_records()` and `pstore_get_backend_records()`. Backends such as `ram.c` and `zone.c` return records that this file materializes. `ftrace.c` provides decode/merge helpers for ftrace records.

## Risks
The filesystem borrows dentry pointers in `pstore_private`, so unlink and backend removal carefully clear them. Record ownership transfers to the filesystem only on successful `pstore_mkfile()`.
