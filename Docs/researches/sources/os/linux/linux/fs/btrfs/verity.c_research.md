# File Research: sources/os/linux/linux/fs/btrfs/verity.c

## Purpose

`verity.c` implements Btrfs' `struct fsverity_operations` backend. It stores fs-verity descriptors and Merkle tree bytes as dedicated Btrfs metadata items in the filesystem tree, while caching Merkle tree pages in the inode mapping at synthetic offsets past EOF.

The file deliberately differs from ext4/f2fs style past-EOF on-disk storage. Btrfs keeps verity data in btree items to avoid changing file size semantics and to fit its existing metadata model.

## On-Disk Layout

Descriptor items use keys of the form:

`[ inode objectid, BTRFS_VERITY_DESC_ITEM_KEY, offset ]`

At offset 0, Btrfs stores `struct btrfs_verity_descriptor_item`, including the descriptor size. Starting at offset 1, it stores the opaque fs-verity descriptor bytes.

Merkle tree items use keys of the form:

`[ inode objectid, BTRFS_VERITY_MERKLE_ITEM_KEY, offset ]`

Their offsets start at 0 and correspond to Merkle tree byte offsets. The payload is opaque to Btrfs.

## Merkle Cache Position

`merkle_file_pos()` computes the synthetic file offset used for caching Merkle tree pages in the inode page cache. It rounds `i_size` up to 64 KiB via `MERKLE_START_ALIGN` and rejects results beyond `s_maxbytes` with `-EFBIG`.

This keeps cached Merkle pages safely beyond the last possible data page, including systems with 64 KiB pages.

## Item Cleanup

`drop_verity_items()` deletes all items for one inode and one verity key type. It repeatedly searches backwards from offset `U64_MAX`, deletes one matching item per transaction, releases the path, and continues until no matching key remains.

`btrfs_drop_verity_items()` removes both descriptor and Merkle item types. It is used before enabling verity and during rollback.

## Item I/O Helpers

`write_key_bytes()` writes an arbitrary byte range into a sequence of Btrfs items. It inserts items of up to 2048 bytes, with keys advancing by the copied byte count. Each item is inserted and written in its own transaction.

`read_key_bytes()` reads a sequence of items starting at a requested offset. It supports three modes:

- count-only mode when `dest` is NULL.
- copying into a caller buffer.
- copying into a folio when reading Merkle tree pages.

It accepts starting in the middle of the first item, then requires subsequent items to be sequential. Short reads are allowed when items end before the requested length.

## Orphan and Rollback Handling

Enabling fs-verity can write a large Merkle tree, so Btrfs protects the whole operation with an orphan item.

`del_orphan()` removes the verity orphan item but ignores inodes with zero links and treats `-ENOENT` as success. This avoids conflicting with other orphan users such as unlink or `O_TMPFILE`.

`rollback_verity()` is called when enablement fails. It truncates cached Merkle pages past EOF, clears `BTRFS_INODE_VERITY_IN_PROGRESS`, drops verity items, clears the inode's verity ro flag, updates the inode, and deletes the orphan. If rollback cleanup itself fails, it reports filesystem errors because partial verity state is not recoverable.

## Enabling Verity

`btrfs_begin_enable_verity()` is the fsverity begin hook. It requires the inode lock, rejects encrypted files, rejects concurrent verity enablement with `-EBUSY`, drops stale verity items, adds an orphan item, and sets the in-progress runtime flag.

`finish_verity()` writes the descriptor-size item, writes the descriptor bytes, starts a transaction, sets `BTRFS_INODE_RO_VERITY`, syncs VFS inode flags, updates the inode item, deletes the orphan, clears the in-progress bit, and sets the filesystem read-only compatible `VERITY` bit.

`btrfs_end_enable_verity()` is the fsverity end hook. If fsverity passes a NULL descriptor, it rolls back. Otherwise it calls `finish_verity()` and rolls back on failure.

## Descriptor Reads

`btrfs_get_verity_descriptor()` reads the descriptor header item at offset 0, validates reserved fields and size, supports a size-query call when `buf_size == 0`, rejects undersized buffers with `-ERANGE`, then reads the descriptor blob from offset 1. It returns the true descriptor size or a negative error.

## Merkle Tree Reads and Writes

`btrfs_read_merkle_tree_page()` maps a Merkle page index to the synthetic post-EOF page-cache index. It first checks for an existing up-to-date folio. If absent, it allocates and adds a folio, reads up to one page of Merkle bytes from `BTRFS_VERITY_MERKLE_ITEM_KEY` items, zero-fills any short read, marks the folio uptodate, and returns the page.

`btrfs_write_merkle_tree_block()` validates that the synthetic Merkle cache position plus the requested Merkle range fits within `s_maxbytes`, then writes the block bytes into Merkle items through `write_key_bytes()`.

## fsverity Operations Table

`btrfs_verityops` wires Btrfs into the VFS fs-verity layer:

- `begin_enable_verity`
- `end_enable_verity`
- `get_verity_descriptor`
- `read_merkle_tree_page`
- `write_merkle_tree_block`

## Filesystem Role

This file is the bridge between generic fs-verity and Btrfs metadata. It handles Btrfs-specific storage, transactions, orphan protection, page-cache placement, rollback, and inode flag persistence while leaving descriptor and Merkle payload interpretation to the generic fs-verity layer.
