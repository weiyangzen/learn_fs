# File Research: sources/os/linux/linux/fs/ubifs/file.c

Read completely: 1666 lines.

This file implements UBIFS regular-file, symlink, device-node inode, file, mmap, and address-space operations. It owns folio read/write behavior, write budgeting, dirty-folio accounting, writeback ordering, truncation, setattr, fsync, time updates, mmap write faults, and symlink resolution.

Main entry points: `ubifs_setattr`, `ubifs_fsync`, `ubifs_update_time`, `ubifs_file_address_operations`, `ubifs_file_inode_operations`, `ubifs_symlink_inode_operations`, and `ubifs_file_operations`.

Key read behavior: `read_block` looks up data nodes in the TNC, treats `-ENOENT` as holes, decrypts encrypted nodes, decompresses data into folios, validates logical sizes, and zero-fills short blocks. `do_readpage` handles multi-block folios and beyond-EOF reads. Bulk-read can read consecutive data nodes from one LEB into a shared buffer after detecting sequential access.

Key write behavior: `write_begin` has fast and slow budgeting paths to avoid deadlocking on locked folios when budgeting may force writeback. `PG_private` tracks UBIFS-budgeted dirty folios, while `PG_checked` distinguishes holes/new-page budgeting from existing-page changes. `write_end`, invalidation, release, and writeback release or convert the corresponding budgets and maintain `dirty_pg_cnt`.

Writeback and size consistency: `ubifs_writepage` avoids writing data beyond the last synchronized inode size unless it first writes the inode, preventing committed data nodes beyond on-flash inode size after power loss. Truncation writes a dirty partial last block before journaling a truncate node when needed.

Other VFS behavior: `ubifs_fsync` writes dirty ranges, optionally writes the inode, and flushes write buffers by inode. `ubifs_write_iter` updates mtime/ctime before generic writes. `ubifs_vm_page_mkwrite` budgets mmap writes before folio lock, handles races with truncation, dirties the folio, and updates timestamps. Symlink operations route encrypted symlinks through fscrypt.

Important interactions: depends on `compress.c` for decompression, `crypto.c` for decryption, journal helpers for data and truncate records, budgeting helpers for page/inode reservations, and debug checks for synchronized inode size.

Reliability notes: this is one of UBIFS’s most budget-sensitive files. Correctness depends on matching every dirty-folio state transition with the correct budget release and on preserving `ui_size`, `synced_i_size`, and VFS `i_size` ordering across writeback, append, mmap, and truncate races.
