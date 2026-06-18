# File Research: sources/windows/winbtrfs/src/send.c

## Purpose

`send.c` implements WinBtrfs subvolume send support. It builds Btrfs send-stream commands for a read-only subvolume, optionally comparing it against a parent snapshot for incremental sends, and exposes the generated stream through a buffered asynchronous kernel worker.

## Main State

The central `send_context` ties together:

- Filesystem state: `Vcb`, target `root`, optional `parent`, optional clone roots.
- Output stream buffer: `data`, `datalen`, `buffer_event`, and `send_info`.
- Directory/path tracking:
  - `send_dir` records inode, parent, name, timestamps, dummy/orphan status, and deleted children.
  - `orphan` tracks temporary names used while rename/delete ordering is resolved.
  - `ref` stores current and old inode references.
  - `pending_rmdir` delays directory removal until children have been processed.
- Per-inode accumulation in `lastinode`:
  - inode metadata, old metadata, current path, orphan/dir pointers
  - current/old refs
  - current/old extent lists

The file uses `MAX_SEND_WRITE` of 48 KiB and a 1 MiB `SEND_BUFFER_LENGTH`; the allocation gives extra space for write command overhead.

## Send Command Encoding

Low-level helpers build the stream format:

- `send_command()` reserves a `btrfs_send_command` with a command id and zero checksum.
- `send_add_tlv()` appends typed-length-value fields.
- `send_command_finish()` fills command length and CRC32C checksum.
- `send_add_tlv_path()`, `find_path_len()`, and `find_path()` construct slash-separated paths from tracked directory parents.
- `send_subvol_header()` emits either `BTRFS_SEND_CMD_SUBVOL` or `BTRFS_SEND_CMD_SNAPSHOT`, including target UUID/transid and parent clone UUID/transid when applicable.

Metadata command helpers emit `CHOWN`, `CHMOD`, `UTIMES`, `TRUNCATE`, `UNLINK`, and `RMDIR`.

## Path, Ref, and Orphan Handling

The implementation has substantial ordering logic to make generated operations replayable:

- `get_orphan_name()` generates unique temporary root-level names of the form `o<inode>-<generation>-<index>`, checking current and parent roots for collisions.
- `find_send_dir()` locates or creates `send_dir` records, using parent snapshot refs when available and dummy orphan paths otherwise.
- `send_inode_ref()` and `send_inode_extref()` parse `INODE_REF` and `INODE_EXTREF` items into current or old ref lists.
- `found_path()` resolves an orphaned inode by renaming it into its real path, or links another name to the existing path.
- `look_for_collision()` checks the parent snapshot for path collisions before renames/links.
- `make_file_orphan()` renames colliding files/directories to temporary orphan names or records deleted non-directory children.
- `flush_refs()` compares current and old refs, handles new paths, deletes old paths, moves/renames directories, delays non-empty directory removals, and emits parent directory timestamp restoration when needed.

This logic is necessary because Btrfs tree item order does not always match a safe replay order for directory renames and deletions.

## Inode Processing

`send_inode()` initializes `lastinode` from an `INODE_ITEM`, detects deletes, records new-vs-existing state, and emits creation commands for new objects:

- `MKSOCK`
- `SYMLINK`
- `MKNOD`
- `MKDIR`
- `MKFIFO`
- `MKFILE`

For symlinks, `send_read_symlink()` reads inline extent data and adds `BTRFS_SEND_TLV_PATH_LINK`. New objects are first created under orphan names, then moved or linked into final paths after refs are known.

`finish_inode()` flushes refs and extents, emits truncate/chown/chmod/utimes for non-deleted inodes, frees accumulated extent/ref state, and processes pending directory removals whose last child inode has now passed.

## Extent Handling

File data is accumulated through `send_extent_data()` and emitted by `flush_extents()`.

Key behavior:

- It validates extent item sizes, compression, encryption, and encoding.
- It skips symlink extent data.
- It records non-empty inline and regular extents for current and parent roots.
- For incremental sends, `add_ext_holes()` inserts sparse hole extents and `sync_ext_cutoff_points()` splits current/old extents so comparable ranges align.
- `divide_ext()` splits inline or regular extents at a requested logical length.
- `try_clone()` and `try_clone_edr()` inspect extent backrefs and clone roots to emit `BTRFS_SEND_CMD_CLONE` when a matching sector-aligned source extent can be found.
- Inline uncompressed data is emitted directly.
- Inline compressed data is decompressed before sending.
- Regular sparse extents are emitted as zero-filled writes.
- Regular uncompressed extents are read from disk with checksums unless `BTRFS_INODE_NODATASUM` is set.
- Regular compressed extents are read, decompressed using zlib/LZO/ZSTD helpers, then emitted in write chunks.

Unsupported or unknown compression/encryption/encoding paths return errors rather than generating a questionable stream.

## Xattrs

`send_xattr()` emits xattr changes after refs have been flushed so a valid path exists:

- Current-only xattrs become `BTRFS_SEND_CMD_SET_XATTR`.
- Parent-only xattrs become `BTRFS_SEND_CMD_REMOVE_XATTR`.
- Current+parent xattrs are compared by name and value; only changed, added, or removed xattrs produce commands.
- Xattrs are parsed from `DIR_ITEM` payloads with truncation checks.

## Worker Thread

`send_thread()` is the asynchronous producer.

Main flow:

1. Increments send operation counters for target, parent, and clone roots.
2. Acquires the tree lock exclusively, flushes subvolume FCBs, writes pending filesystem state if needed, frees cached trees, then downgrades to shared.
3. Traverses the target root and, for incremental sends, the parent root in key order.
4. Uses `skip_to_difference()` when both traversals are in the same tree block.
5. Dispatches by item type:
   - `TYPE_INODE_ITEM` -> `send_inode`
   - `TYPE_INODE_REF` -> `send_inode_ref`
   - `TYPE_INODE_EXTREF` -> `send_inode_extref`
   - `TYPE_EXTENT_DATA` -> `send_extent_data`
   - `TYPE_XATTR_ITEM` -> `send_xattr`
6. Calls `finish_inode()` when moving to the next inode.
7. Periodically releases the tree lock and signals the reader when the send buffer exceeds the threshold.
8. On completion or error, signals the buffer, stores status, frees all context state, removes the send from `Vcb->send_ops`, decrements counters, and terminates the system thread.

`wait_for_flush()` handles the producer/consumer handshake, preserves traversal keys, reacquires the tree lock, and verifies the read-only subvolume did not change while the lock was released.

## Public Entry Points

- `send_subvol(...)`
  - Validates the file object, target is a subvolume root, caller has `SE_MANAGE_VOLUME_PRIVILEGE`, and target/parent/clone roots are read-only unless the volume itself is read-only.
  - Accepts optional parent and clone handles, including 32-bit process handle layouts on Win64.
  - Allocates `send_context`, stream buffer, and `send_info`.
  - Emits the subvolume/snapshot header immediately.
  - Starts `send_thread()` and links the send operation to the CCB and VCB.
- `read_send_buffer(...)`
  - Requires `SE_MANAGE_VOLUME_PRIVILEGE`.
  - Waits for producer data, copies up to caller length, shifts remaining bytes if partially consumed, and signals the producer when the buffer is drained.
  - Returns stored failure status or `STATUS_END_OF_FILE` when no send remains.

## Integration

This file depends on core WinBtrfs tree traversal, item parsing, extent backref parsing, checksum loading, compression decompression, disk reads, FCB flushing, locking, and IOCTL-facing `send_info` state defined elsewhere in the driver. It is the bridge between on-disk Btrfs metadata and the userspace-readable Btrfs send protocol stream.

## Notable Risks and Edge Cases

- Correctness depends heavily on read-only roots remaining stable; the code explicitly treats key changes after buffer flush as internal errors.
- The path/orphan logic is complex and stateful; replay correctness relies on maintaining sorted orphan/dir/pending-rmdir lists.
- Many allocations happen while generating a send stream; low-memory paths usually return `STATUS_INSUFFICIENT_RESOURCES` but must unwind partially accumulated state.
- Clone detection is opportunistic. If no valid clone source is found, data is sent as writes.
- Compressed extents are decompressed before send writes; unsupported compression returns `STATUS_NOT_IMPLEMENTED`.
