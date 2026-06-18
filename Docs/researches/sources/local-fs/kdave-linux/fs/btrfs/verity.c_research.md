# File Research: sources/local-fs/kdave-linux/fs/btrfs/verity.c

## Purpose

`verity.c` implements Btrfs support for Linux fs-verity through `struct fsverity_operations`. It stores fs-verity descriptors and Merkle tree data as dedicated Btrfs items in the file's filesystem tree, rather than storing them as file data past EOF.

The file handles verity enablement, rollback, descriptor read/write, Merkle tree item read/write, page-cache integration for Merkle pages, and cleanup of incomplete verity state.

## On-Disk Item Model

Btrfs uses two item key types under the inode objectid:

- Descriptor items: `[ inode objectid, BTRFS_VERITY_DESC_ITEM_KEY, offset ]`
- Merkle tree items: `[ inode objectid, BTRFS_VERITY_MERKLE_ITEM_KEY, offset ]`

Descriptor offset `0` stores `struct btrfs_verity_descriptor_item`, which records the descriptor size and reserved metadata. Descriptor bytes start at offset `1`.

Merkle tree items start at offset `0` and store opaque Merkle tree bytes. Btrfs does not interpret the Merkle tree data.

## Merkle Cache Position

`merkle_file_pos()` computes a synthetic file offset for caching Merkle tree pages in the inode page cache. It rounds `i_size` up to `MERKLE_START_ALIGN` (`65536`) so Merkle pages sit past EOF even on systems with 64K pages. It checks against `s_maxbytes` and returns `-EFBIG` on overflow.

This offset is for cache indexing only; Merkle data is stored in B-tree items.

## Item Drop And Byte IO Helpers

`drop_verity_items()` walks backward through all items of a key type for the inode and deletes them one by one in small transactions. It is used before enabling verity and during rollback.

`btrfs_drop_verity_items()` drops both descriptor and Merkle item types.

`write_key_bytes()` writes arbitrary bytes into one or more Btrfs items, inserting up to 2K bytes per item. Each item key uses the inode objectid, requested key type, and current byte offset. It starts and ends a transaction per inserted item.

`read_key_bytes()` reads sequential bytes from items of a given key type and offset. With `dest == NULL`, it counts bytes without copying. With `dest_folio`, it copies into a mapped folio and enables forward readahead on the path. It supports reads beginning in the middle of an item and stops on holes, non-sequential offsets, key mismatch, or tree end.

## Orphan Handling And Rollback

Verity enablement can write many Merkle items and may fail partway through. Btrfs guards the operation with an orphan item and a runtime `BTRFS_INODE_VERITY_IN_PROGRESS` bit.

`del_orphan()` deletes the verity orphan item but ignores zero-link inodes and treats `-ENOENT` as success.

`rollback_verity()` is called when enablement fails. It requires the inode lock, truncates cached pages past `i_size`, clears the in-progress bit, drops verity items, clears `BTRFS_INODE_RO_VERITY`, syncs inode flags, updates the inode, and deletes the orphan item. If rollback itself fails, it reports a filesystem error because the partial verity state may be unrecoverable.

## Enable Verity Flow

`btrfs_begin_enable_verity()` is the fs-verity begin hook. It rejects encrypted inodes, rejects concurrent enablement with `-EBUSY`, drops any stale verity items, adds an orphan item in a transaction, and sets `BTRFS_INODE_VERITY_IN_PROGRESS`.

`btrfs_end_enable_verity()` is the fs-verity end hook. If `desc == NULL`, fs-verity is reporting an earlier failure, so Btrfs rolls back. Otherwise it calls `finish_verity()` and rolls back if finalization fails.

`finish_verity()` writes the descriptor header item, writes the descriptor blob, starts a transaction, sets `BTRFS_INODE_RO_VERITY`, syncs inode flags, updates the inode, deletes the orphan, clears the in-progress bit, and sets the filesystem read-only compatibility bit `VERITY`.

## Descriptor Reading

`btrfs_get_verity_descriptor()` reads the descriptor header at descriptor key offset `0`, validates reserved fields, obtains the true descriptor size, and supports fs-verity's two-pass API:

- `buf_size == 0`: return descriptor size.
- `buf_size < true_size`: return `-ERANGE`.
- Otherwise read descriptor bytes from offset `1`.

It returns `-EUCLEAN` on invalid descriptor header state, `-EIO` on short descriptor reads, or the descriptor size on success.

## Merkle Tree Page Read

`btrfs_read_merkle_tree_page()` reads and caches one Merkle tree page for fs-verity. It translates the fs-verity page index into the synthetic page-cache index past EOF, then:

1. Looks for an existing folio in the inode mapping.
2. If present and uptodate, returns the requested page.
3. If present but not uptodate after locking, returns `-EIO`.
4. Allocates and adds a new folio with GFP constraints avoiding filesystem recursion.
5. Reads up to one page of Merkle bytes from `BTRFS_VERITY_MERKLE_ITEM_KEY` items.
6. Zero-fills any short read, marks the folio uptodate, unlocks it, and returns the page.

It checks both synthetic file position and page offset against `s_maxbytes`.

## Merkle Tree Write

`btrfs_write_merkle_tree_block()` is the fs-verity write hook for a Merkle tree block. It validates that the synthetic cache position plus Merkle offset and size do not exceed `s_maxbytes`, then writes the block into `BTRFS_VERITY_MERKLE_ITEM_KEY` items at the given Merkle byte offset.

## Exported Operations

`btrfs_verityops` binds Btrfs to the generic fs-verity layer:

- `begin_enable_verity = btrfs_begin_enable_verity`
- `end_enable_verity = btrfs_end_enable_verity`
- `get_verity_descriptor = btrfs_get_verity_descriptor`
- `read_merkle_tree_page = btrfs_read_merkle_tree_page`
- `write_merkle_tree_block = btrfs_write_merkle_tree_block`

## Dependencies

The file depends on Linux fs-verity, folio/page-cache, xattr/security includes, and Btrfs transaction/orphan/inode/accessor APIs. It uses `btrfs_start_transaction()`, `btrfs_insert_empty_item()`, `btrfs_del_items()`, `btrfs_truncate_item()`, `btrfs_update_inode()`, `btrfs_orphan_add()`, and `btrfs_del_orphan_item()`.

## Invariants And Risks

The central invariant is that a verity inode must not be left with partial descriptor/Merkle state unless it is guarded by the in-progress bit and orphan cleanup path. Successful finalization must atomically make the inode verity-read-only from the filesystem perspective and remove the orphan.

Risk areas include rollback failure, short or non-sequential item reads, synthetic page-cache index overflow, stale cached Merkle pages after failed enablement, and future encryption support because descriptor/Merkle items are metadata items rather than file data.
