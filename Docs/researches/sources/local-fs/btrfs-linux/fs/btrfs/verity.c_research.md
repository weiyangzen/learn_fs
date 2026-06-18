# File Research: sources/local-fs/btrfs-linux/fs/btrfs/verity.c

Implements Btrfs support for Linux fs-verity operations by storing verity descriptors and Merkle tree bytes as dedicated items in the inode's filesystem tree.

Key entry points:
- `btrfs_drop_verity_items()` removes all descriptor and Merkle tree items for an inode.
- `btrfs_get_verity_descriptor()` reads and validates the Btrfs descriptor-size wrapper and generic fs-verity descriptor blob.
- `btrfs_verityops` wires Btrfs into fs-verity with begin/end enable, descriptor read, Merkle page read, and Merkle block write callbacks.
- `btrfs_begin_enable_verity()` prepares enabling by rejecting encrypted files, dropping stale verity items, adding an orphan item, and setting `BTRFS_INODE_VERITY_IN_PROGRESS`.
- `btrfs_end_enable_verity()` finalizes or rolls back depending on whether fs-verity supplies a descriptor.
- `btrfs_read_merkle_tree_page()` reads Merkle bytes from Btrfs items into page-cache folios positioned past EOF.
- `btrfs_write_merkle_tree_block()` writes Merkle blocks into Btrfs verity Merkle items.

Core mechanics:
- Descriptor metadata uses keys `[ino, BTRFS_VERITY_DESC_ITEM_KEY, offset]`; offset `0` stores `struct btrfs_verity_descriptor_item`, and offset `1` onward stores the opaque fs-verity descriptor.
- Merkle data uses keys `[ino, BTRFS_VERITY_MERKLE_ITEM_KEY, offset]`, where offsets are byte offsets into the Merkle tree.
- `write_key_bytes()` writes arbitrary byte ranges into multiple Btrfs items, splitting inserts into at most 2 KiB chunks for leaf-size friendliness.
- `read_key_bytes()` reads sequential item payloads from a key type and offset, supporting count-only mode, buffer-copy mode, and folio-copy mode with forward readahead.
- `merkle_file_pos()` rounds `i_size` up to a 64 KiB boundary and uses that logical position only for page-cache placement of Merkle pages.
- `drop_verity_items()` walks backward from offset `U64_MAX` deleting all items of a given verity key type for the inode.
- Enable is protected by a normal orphan item so interrupted or failed verity setup can be cleaned up rather than leaving partial Merkle/descriptor state.
- `finish_verity()` writes the descriptor wrapper/blob, sets `BTRFS_INODE_RO_VERITY`, syncs inode flags, deletes the orphan item, clears the in-progress bit, and sets the filesystem read-only compatible `VERITY` bit.
- `rollback_verity()` truncates cached Merkle pages, clears in-progress state, drops verity items, removes the inode verity flag, updates the inode, and deletes the verity orphan.

Important invariants:
- Verity enable requires the inode lock; begin/end/rollback assert this.
- Btrfs currently rejects fs-verity enable on encrypted inodes.
- Descriptor wrapper reserved fields must remain zero, and descriptor size must fit in `INT_MAX`.
- A successful descriptor read must return exactly the true descriptor size; short reads become `-EIO`.
- Merkle page-cache positions must not exceed `s_maxbytes`; overflow checks guard both reads and writes.
- Partial Merkle pages are zero-filled after short reads before being marked uptodate.
- Rollback errors are treated as filesystem errors because partial verity state could otherwise persist.

Filesystem relevance:
- This file integrates authenticity verification for Btrfs regular files while preserving Btrfs' normal inode size semantics by storing fs-verity metadata as btree items instead of past-EOF file extents.

Notable risks:
- Writing Merkle data can be lengthy and space-consuming, so failure paths are intentionally complex and depend on orphan cleanup.
- `write_key_bytes()` and `read_key_bytes()` require strictly sequential item offsets for descriptor/Merkle blobs; gaps produce short reads or failure at higher layers.
- Cache placement past EOF is synthetic; overflow and truncation interactions must remain aligned with fs-verity expectations.
- Future Btrfs encryption support must account for encrypting descriptor and Merkle items, as noted in the file comments.
