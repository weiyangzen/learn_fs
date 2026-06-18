# File Research: sources/os/linux/linux-stable/fs/ext4/inline.c

## Purpose

Implements ext4 inline data support: storing small regular-file data, symlink data, and small directory contents directly inside the inode body. Inline data occupies `i_block` first, then an in-inode extended attribute named `system.data` when extra inode xattr space is available.

## Storage Model

- `EXT4_MIN_INLINE_DATA_SIZE` is the fixed inline payload held in `struct ext4_inode.i_block`.
- Additional inline payload is stored as the value of the in-inode xattr `EXT4_XATTR_INDEX_SYSTEM:"data"`.
- `EXT4_I(inode)->i_inline_off` points to the xattr entry inside the raw inode.
- `EXT4_I(inode)->i_inline_size` is total inline capacity currently available.
- Inline directories store only the parent inode number for `..` in the first 4 bytes; `.` and `..` entries are synthesized during lookup/readdir/tree conversion.

## Main Responsibilities

- Discover inline data at inode load through `ext4_find_inline_data_nolock()`.
- Compute available inline capacity with `ext4_get_max_inline_size()` and `get_max_inline_xattr_value_size()`.
- Create, grow, shrink, destroy, and convert inline data under journaling.
- Serve buffered reads and writes for inline files.
- Support inline directory insert, search, delete, emptiness check, and readdir.
- Convert inline data to normal extent/indirect block storage when inline capacity is exceeded.
- Expose inline extents through iomap reporting.

## Key Functions and Flows

- `ext4_read_inline_data()` copies from raw inode `i_block` and then from the xattr value area.
- `ext4_write_inline_data()` writes to the same two-part layout, assuming inline metadata has already been prepared and journal access acquired.
- `ext4_create_inline_data()` inserts the `system.data` xattr, zeroes `i_block`, clears `EXT4_INODE_EXTENTS`, sets `EXT4_INODE_INLINE_DATA`, and marks the inode dirty.
- `ext4_update_inline_data()` expands the xattr value while preserving previous xattr content.
- `ext4_prepare_inline_data()` checks `EXT4_STATE_MAY_INLINE_DATA`, recomputes inline metadata, and either creates or updates inline storage.
- `ext4_destroy_inline_data_nolock()` removes the inline xattr, clears inline state, zeroes inode data fields, and reinitializes extent state where appropriate.
- `ext4_readpage_inline()` loads inline file data into folio 0 and zero-fills other pages.
- `ext4_generic_write_inline_data()` prepares folio 0 plus a journal handle for inline write_begin paths.
- `ext4_write_inline_data_end()` copies user data from the folio back into the inode/xattr inline area, updates size, handles partial-copy orphan cleanup, and stops the journal handle.
- `ext4_convert_inline_data_to_extent()` and `ext4_da_convert_inline_data_to_extent()` migrate inline data into page cache and normal block mapping paths for non-delalloc and delalloc writes.
- `ext4_convert_inline_data_nolock()` performs immediate conversion to a real block for directories or non-delalloc conversion, with restore-on-error logic.
- `ext4_inline_data_truncate()` shrinks the inline xattr value and clears truncated bytes from `i_block`.
- `ext4_inline_data_iomap()` reports an `IOMAP_INLINE` mapping pointing into the inode table buffer.

## Inline Directory Handling

- `ext4_try_create_inline_dir()` initializes a new inline directory with parent inode metadata and an empty fake dirent spanning remaining inline space.
- `ext4_try_add_inline_entry()` first inserts into the `i_block` region, then grows into xattr inline space, and finally converts to block-based directory storage if full.
- `ext4_find_inline_entry()` searches both inline regions.
- `ext4_delete_inline_entry()` removes an inline dirent via generic dirent deletion after journal write access.
- `ext4_read_inline_dir()` synthesizes stable offsets for `.` and `..` so userspace cookies resemble a normal block directory.
- `ext4_inlinedir_to_tree()` feeds inline entries into htree readdir state, synthesizing `.` and `..`.
- `empty_inline_dir()` validates inline dirents and returns whether any real child entries remain.

## Locking and Journaling

- Uses `xattr_sem` for inline xattr metadata stability.
- Uses `i_data_sem` while destroying or converting inline layout.
- Acquires journal write access before mutating raw inode/xattr storage.
- Uses orphan list cleanup on failed extending writes or conversion paths that allocated blocks beyond `i_size`.

## Important Edge Cases

- Inline xattr entries referring to external xattr inodes are treated as corruption.
- Inline size larger than `PAGE_SIZE` during read is reported as corruption.
- Conversion validates inline directory entries before writing them into a real directory block.
- Restore path attempts to recreate inline data after failed conversion to avoid data loss.
- `EXT4_STATE_MAY_INLINE_DATA` distinguishes files still eligible for inline storage from files already being converted through delayed allocation.
