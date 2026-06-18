# File Research: sources/os/linux/linux-stable/fs/btrfs/verity.c

## Scope

This file integrates Btrfs with fs-verity. It stores verity descriptors and Merkle tree data as dedicated Btrfs tree items, manages enable/rollback/finalization with orphan protection, and implements the `fsverity_operations` callbacks.

## Public And Internal APIs Covered

- Exported to Btrfs: `btrfs_drop_verity_items()`, `btrfs_get_verity_descriptor()`, `btrfs_verityops`.
- fs-verity callbacks: begin enable, end enable, get descriptor, read Merkle tree page, write Merkle tree block.
- Internal helpers: `merkle_file_pos()`, `drop_verity_items()`, `write_key_bytes()`, `read_key_bytes()`, `del_orphan()`, `rollback_verity()`, `finish_verity()`.

## Control Flow And Behavior

- Verity descriptor items use key type `BTRFS_VERITY_DESC_ITEM_KEY`; offset `0` stores a Btrfs descriptor-size item and offsets starting at `1` store the fs-verity descriptor blob.
- Merkle tree items use key type `BTRFS_VERITY_MERKLE_ITEM_KEY`, indexed from byte offset `0` in the Merkle tree.
- Merkle pages are cached in the inode mapping at a synthetic file position: file size rounded up to 64 KiB, ensuring the cache range is past EOF.
- Enabling verity rejects encrypted files, drops stale verity items, adds an orphan item, and sets `BTRFS_INODE_VERITY_IN_PROGRESS`.
- Merkle blocks are written as Btrfs items via `write_key_bytes()`, split into chunks up to 2 KiB.
- Finalization writes descriptor metadata and descriptor bytes, sets `BTRFS_INODE_RO_VERITY`, updates inode flags, deletes the orphan item, sets the filesystem read-only compat verity bit, and clears the in-progress flag.
- If fs-verity signals failure or finalization fails, rollback truncates cached Merkle pages, clears in-progress state, drops verity items, clears the inode verity flag, updates the inode, and deletes the orphan.
- Descriptor reads support the fs-verity two-pass size-then-data pattern and validate reserved fields and descriptor size.
- Merkle page reads populate the page cache from tree items, zero-fill short final pages, and return cached pages when already uptodate.

## State And Data Structures

- Uses inode runtime flag `BTRFS_INODE_VERITY_IN_PROGRESS` and read-only inode flag `BTRFS_INODE_RO_VERITY`.
- Uses `struct btrfs_verity_descriptor_item` to store descriptor size and reserved fields.
- Uses Btrfs item keys under the file inode objectid for both descriptor and Merkle data.
- Uses orphan items to recover or clean up interrupted verity enable operations.

## Dependencies

- Linux fs-verity API, folio/page-cache APIs, xattr/security includes, inode locking, and mapping allocation constraints.
- Btrfs transaction, orphan, tree item, inode update, extent-buffer read/write, and filesystem compat-ro feature helpers.

## Risks And Invariants

- Btrfs stores verity data outside file size, unlike ext4/f2fs, so cache-position overflow checks against `s_maxbytes` are required.
- Rollback errors are treated as filesystem-level errors because partially written verity metadata would be unsafe.
- `read_key_bytes()` requires sequential item offsets after the first copied item; gaps intentionally produce short reads.
- Orphan handling intentionally ignores zero-link inodes because unlink/tmpfile paths own their own orphan state.
- Encryption is currently unsupported for Btrfs fs-verity in this implementation.
