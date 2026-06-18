# File Research: sources/os/linux/linux/fs/nilfs2/file.c

This file provides regular file operations, fsync handling, mmap write-fault handling, and regular-file inode operation tables.

Fsync:
- `nilfs_sync_file()` checks whether the inode is dirty.
- For datasync, it constructs a dsync segment covering the requested byte range.
- For full fsync, it constructs a normal segment.
- It then flushes the underlying NILFS device.

Memory-mapped writes:
- `nilfs_page_mkwrite()` handles writable page faults.
- It rejects faults near disk-full state with `VM_FAULT_SIGBUS`.
- It validates folio mapping, size, and uptodate state under pagefault protection.
- If the folio is not fully mapped, it starts a NILFS transaction, updates file time, calls `block_page_mkwrite()` with `nilfs_get_block()` to allocate holes, marks newly dirtied file blocks, and commits.
- It waits for writeback before returning because NILFS recovery relies on checksums including data blocks.

Operation tables:
- `nilfs_file_vm_ops` uses generic filemap fault/map-pages plus NILFS page_mkwrite.
- `nilfs_file_operations` provides generic read/write, ioctl, mmap prepare, open, fsync, splice, and lease operations.
- `nilfs_file_inode_operations` provides setattr, permission, fiemap, and file attribute get/set hooks.

Important invariants:
- Mmap write faults must run inside NILFS transaction context when allocating holes.
- Dirty page accounting feeds NILFS segment construction.
- Write faults wait for writeback even when the backing device would not require stable writes.
