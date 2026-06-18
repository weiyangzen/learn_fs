# File Research: sources/os/linux/linux-stable/fs/ubifs/file.c

UBIFS regular-file, symlink, address-space, writeback, mmap, fsync, setattr, and file operation implementation.

Key responsibilities:
- Implements `ubifs_file_address_operations`, `ubifs_file_inode_operations`, `ubifs_symlink_inode_operations`, and `ubifs_file_operations`.
- Reads data nodes from TNC, decrypts if needed, decompresses into folios, and zero-fills holes/tails.
- Budgets dirty folios/pages before writeback because UBIFS must reserve flash space before data reaches media.
- Writes dirty folios through `ubifs_jnl_write_data()`.
- Handles truncation, setattr, fsync, timestamp updates, mmap page faults, and encrypted symlink resolution.

Important read path:
- `read_block()` looks up a data key, treats `-ENOENT` as a hole, validates node size, decrypts encrypted data nodes, decompresses into the folio, and zero-fills short blocks.
- `do_readpage()` reads all UBIFS blocks in a folio and marks folios checked when holes are found.
- Bulk-read uses `ubifs_bulk_read()`, `ubifs_do_bulk_read()`, and `populate_page()` to read consecutive data nodes from one LEB when sequential access is detected.

Important write path:
- `ubifs_write_begin()` has a fast path that avoids writeback-triggering budgeting while a folio is locked. On fast budgeting failure it drops the folio and falls back to `write_begin_slow()`.
- Folio state uses private data plus `PG_checked` to distinguish already-budgeted dirty folios, new pages/holes, and existing on-flash pages.
- `ubifs_write_end()` attaches private data, marks folios dirty, updates inode size for append, and marks inode datasync-dirty.
- `ubifs_writepage()` refuses to write pages fully beyond `i_size`, forces inode writeback before writing data beyond `synced_i_size`, and zeroes partial EOF folio tails.
- `do_writepage()` writes one or more UBIFS blocks from a folio and releases the appropriate page budget afterward.

Attribute and sync behavior:
- `do_truncation()` journals truncate nodes and handles dirty partial last folios before journal truncate.
- `do_setattr()` handles non-shrinking size changes and metadata changes with inode budgeting.
- `ubifs_fsync()` writes dirty ranges, writes inode metadata when needed, then flushes write buffers for the inode.
- `ubifs_update_time()` handles atime when enabled; mtime/ctime are controlled explicitly because UBIFS sets `S_NOCMTIME`.

Mmap and symlink behavior:
- `ubifs_vm_page_mkwrite()` budgets before locking the folio, handles truncation races, marks folios dirty, and updates mtime/ctime.
- `ubifs_get_link()` returns stored symlink data directly for plaintext symlinks or delegates to fscrypt for encrypted symlinks.
- `ubifs_symlink_getattr()` adjusts encrypted symlink stat output through fscrypt.

Cross-file links:
- Uses `compress.c` decompression functions and `crypto.c` decrypt helpers.
- Namespace operations in `dir.c` install these operation tables on new inodes.
- Journal calls are central to data persistence and recovery semantics.
- Debug helpers validate synced size and dump bad nodes.

Invariants and risks:
- Budgeting before dirtying is core; dirtying without prior budget is asserted in `ubifs_dirty_folio()`.
- `ui->synced_i_size` prevents committed data nodes from exceeding committed inode size after an unclean reboot.
- The write path has careful deadlock avoidance between locked folios, budgeting, writeback, and `ui_mutex`.
