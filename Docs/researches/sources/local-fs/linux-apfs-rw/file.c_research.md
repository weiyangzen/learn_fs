# File Research: sources/local-fs/linux-apfs-rw/file.c

This file implements regular-file VFS operations, mmap write-fault handling, fsync, clone/remap hooks, and inode operation wiring.

`apfs_page_mkwrite()` handles mmap write faults. It starts a regular APFS transaction, joins the inode, ensures the inode has an exclusive dstream, locks and validates the page, creates page buffers if needed, clears mapped state on existing buffers so APFS CoW allocation can occur, then calls `block_page_mkwrite()` with `apfs_get_new_block`. It marks the page dirty and defers immediate transaction commit because commit would unlock the page too early.

`apfs_file_vm_ops` uses generic filemap fault/map_pages and APFS `page_mkwrite`. `apfs_file_mmap()` verifies that the mapping has a read operation for the kernel era, marks the file accessed, and installs those vm ops.

`apfs_fsync()` currently syncs the whole filesystem transaction with `apfs_sync_fs(sb, true)`. A comment notes this is broad but correct and easy.

Regular file operations include generic llseek/read/write/open, APFS mmap, APFS fsync, file ioctl, copy-file-range support depending on kernel version, APFS remap/clone range support, and splice read/write compatibility choices.

For Linux 5.3 only, `apfs_fiemap()` is provided through `generic_block_fiemap()` for clone testing. `apfs_file_inode_operations` wires getattr, listxattr, setattr, update_time, fileattr get/set on newer kernels, and optional fiemap.

Research relevance: this file is the VFS-facing regular-file adapter. The most important behavior is mmap write CoW integration through transactions and `apfs_get_new_block`.
