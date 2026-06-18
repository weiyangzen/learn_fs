# File Research: sources/windows/reactos/drivers/filesystems/btrfs/send.c

## Role In The Filesystem

`send.c` implements the ReactOS/WinBtrfs Btrfs send-stream producer. It turns a read-only subvolume, optionally compared against a parent snapshot and clone sources, into Btrfs send commands that user mode reads through `read_send_buffer`. The file is in subset A because it sits directly inside the Windows Btrfs filesystem driver and bridges on-disk Btrfs metadata, snapshot differencing, data reads, compression handling, and kernel/user streaming.

The implementation is not a generic serializer alone. It owns the full send operation lifecycle: privilege validation, source/parent/clone validation, background system-thread creation, tree traversal, inode/ref/extent/xattr diffing, data emission, buffer backpressure, cancellation checks, and teardown.

## Main Data Structures

- `send_dir`: tracks known directory inodes, parent links, path names, timestamps, dummy/orphan state, and children already deleted during collision handling.
- `orphan`: tracks temporary orphan names for files or directories that must be created or moved before their final path is safe.
- `deleted_child`: remembers names deleted from a directory so later old refs are not redundantly unlinked.
- `ref`: normalized inode reference collected from `TYPE_INODE_REF` or `TYPE_INODE_EXTREF`, pointing to a `send_dir` plus a name.
- `pending_rmdir`: queues directory removals that must wait until higher-numbered child inodes have been processed.
- `send_ext`: buffered extent metadata copied from `TYPE_EXTENT_DATA` items for later comparison and write/clone emission.
- `send_context`: operation state shared by the producer thread and reader, including root/parent/clone roots, send buffer, directory/orphan lists, pending removals, current inode state, and synchronization objects.

`send_context.lastinode` is the central per-inode accumulator. It tracks whether the current inode is new, deleting, a file, its metadata, old metadata, final path/orphan state, refs/oldrefs, and extents/oldextents.

## Send Command Encoding

The low-level command helpers are:

- `send_command`: reserves and initializes a `btrfs_send_command`.
- `send_command_finish`: fills command length and CRC32C checksum over the command record.
- `send_add_tlv`: appends typed TLV payloads.
- `send_add_tlv_path`: computes a full path from `send_dir` parent links and appends it as a TLV.

Commands emitted include subvolume/snapshot headers, object creation, rename, link, unlink, rmdir, clone, write, truncate, chmod, chown, utimes, set xattr, and remove xattr.

The buffer model uses:

- `MAX_SEND_WRITE = 0xc000`, limiting individual data writes to 48 KiB.
- `SEND_BUFFER_LENGTH = 0x100000`, a 1 MiB producer buffer threshold.
- Extra allocation wiggle room of `SEND_BUFFER_LENGTH + 2 * MAX_SEND_WRITE`.

## Path And Orphan Handling

The send stream must produce valid operations even when Btrfs item order does not match path dependency order. This file handles that with temporary orphan names and dummy directories.

Important helpers:

- `uint64_to_char`: decimal integer formatting for temporary names.
- `get_orphan_name`: creates names like `o<inode>-<generation>-<index>` and probes both current and parent roots to avoid collisions in the subvolume root.
- `add_orphan`: keeps the orphan list sorted by inode.
- `find_send_dir`: resolves or creates `send_dir` objects; when only parent snapshot information is available it may create dummy directories.
- `found_path`: either renames an orphan into its final path or links an additional hardlink to the current inode.

For new inodes, `send_inode` often creates the object first under a temporary orphan name, then later `flush_refs` moves it to the final path once references are known. This allows stream order to remain valid under renames, collisions, hardlinks, and directories whose parents appear later.

## Inode Processing

`send_inode` handles `TYPE_INODE_ITEM` differences and initializes `lastinode`.

Cases include:

- Deleted inode: records old generation, mode, and flags from parent.
- Existing/new inode: records uid, gid, mode, size, timestamps, flags, file classification, and previous metadata if available.
- Subvolume root inode: initializes `root_dir`.
- New non-root inode: emits a creation command under an orphan name:
  - `BTRFS_SEND_CMD_MKSOCK`
  - `BTRFS_SEND_CMD_SYMLINK`
  - `BTRFS_SEND_CMD_MKNOD`
  - `BTRFS_SEND_CMD_MKDIR`
  - `BTRFS_SEND_CMD_MKFIFO`
  - `BTRFS_SEND_CMD_MKFILE`

Symlinks are read via `send_read_symlink`, which expects inline extent data and returns an empty target if symlink data is not inline.

`finish_inode` flushes pending refs and extents, emits truncate/chown/chmod/utimes as needed, handles pending rmdirs, frees per-inode lists, and resets `lastinode`.

## Reference Diffing

`send_inode_ref` and `send_inode_extref` normalize both classic inode refs and extended refs into `ref` entries. They also create dummy/orphan directories when the referenced parent directory has not yet appeared in traversal order.

`flush_refs` is one of the most important routines in the file. It compares current refs against old refs and decides whether to:

- Rename an orphan to a final path.
- Emit hardlink commands.
- Emit rename commands for moved/renamed directories.
- Emit unlink commands for removed refs.
- Emit rmdir commands immediately or queue them in `pending_rmdirs`.
- Move colliding paths out of the way using `make_file_orphan`.

Directory handling is special because directory removes must respect child ordering. The file queries the old parent tree with `get_dir_last_child`, then either removes immediately or queues a `pending_rmdir` keyed by last child inode.

## Extent Diffing And Data Emission

`send_extent_data` collects current and parent extent records for regular files, validating:

- Minimum item sizes.
- No unsupported encryption.
- No unsupported encoding.
- Compression type is none, zlib, LZO, or Zstd.
- Regular extents include `EXTENT_DATA2`.
- Inline extents are large enough for decoded data when uncompressed.

`flush_extents` turns accumulated extents into write or clone commands.

For parent-differential sends:

- `add_ext_holes` inserts synthetic sparse-hole extents so current and old extent lists cover comparable ranges.
- `sync_ext_cutoff_points` splits extents with `divide_ext` so current and old extent boundaries align.
- Unchanged inline or regular extents are skipped.

For changed data:

- Inline uncompressed extents are written directly.
- Inline compressed extents are decompressed before writing.
- Sparse extents emit zero-filled writes.
- Regular uncompressed extents are read from disk in 48 KiB chunks, with checksum loading unless `BTRFS_INODE_NODATASUM` is set.
- Regular compressed extents are read, decompressed into memory, and emitted in 48 KiB writes.

Clone optimization is attempted before raw writes:

- `try_clone` inspects extent backrefs in the extent tree.
- `try_clone_edr` matches backrefs against the parent or supplied clone roots.
- `send_add_tlv_clone_path` reconstructs the source inode path inside the clone root.
- A clone command is emitted only when offsets and lengths meet sector alignment constraints.

## Xattr Diffing

`send_xattr` emits xattr operations for `TYPE_XATTR_ITEM`.

Cases:

- Current only: emit `BTRFS_SEND_CMD_SET_XATTR` for each packed `DIR_ITEM`.
- Parent only: emit `BTRFS_SEND_CMD_REMOVE_XATTR`.
- Both: build an `xattr_cmp` list, match names, compare values, then emit set/remove operations only for differences.

The xattr parser carefully walks packed `DIR_ITEM` records and validates each record length before use.

## Traversal And Snapshot Differencing

`send_thread` performs the actual send generation.

Initial setup:

- Increments `send_ops` counters on root, parent, and clone roots.
- Acquires the tree lock exclusively.
- Flushes subvolume FCBs.
- Forces pending writes through `do_write` if needed.
- Frees cached trees.
- Converts the tree lock to shared mode for traversal.

Without a parent snapshot, it walks the root tree in key order and processes relevant item types.

With a parent snapshot, it walks both trees in sorted key order:

- Uses `skip_to_difference` to skip shared tree blocks by address.
- Handles equal keys as modified/same items.
- Handles keys only in the current root as additions.
- Handles keys only in the parent root as deletions.
- Finishes an inode whenever traversal moves to a higher object id.

Relevant item types:

- `TYPE_INODE_ITEM`
- `TYPE_INODE_REF`
- `TYPE_INODE_EXTREF`
- `TYPE_EXTENT_DATA`
- `TYPE_XATTR_ITEM`

A special inode-item generation comparison detects replacement of an inode with the same object id but different generation, treating the old inode as deleted before creating the new one.

## Buffering, Synchronization, And Cancellation

The producer thread and user reader coordinate with two events:

- `context->buffer_event`: producer signals data is available.
- `send->cleared_event`: reader signals buffer space has been consumed.

`wait_for_flush` releases the tree lock while waiting for the reader, then reacquires it and re-finds traversal keys. It verifies that readonly subvolumes did not change by checking the key found after reacquisition.

Cancellation is checked after buffer waits and major flush operations through `send->cancelling`.

`read_send_buffer`:

- Validates the caller and `SE_MANAGE_VOLUME_PRIVILEGE`.
- Waits for `buffer_event`.
- Copies up to caller buffer length.
- Slides remaining data down if partially consumed.
- Clears the producer buffer and signals `cleared_event` when fully consumed.
- Returns `STATUS_END_OF_FILE` after the send completes successfully, or the stored send status on failure.

## Public Entry Points

`send_subvol` starts a send operation. It validates:

- File object and FCB/CCB presence.
- Caller has `SE_MANAGE_VOLUME_PRIVILEGE`.
- Target is a subvolume root and not the filesystem root.
- Target is readonly unless the mounted Vcb is readonly.
- Optional parent handle is a different readonly subvolume on the same device.
- Optional clone handles are readonly subvolume roots on the same device.
- No send is already active on the CCB.

It allocates `send_context`, send buffer, `send_info`, initializes lists/events, emits the subvolume/snapshot header, creates the kernel send thread, registers it in `Vcb->send_ops`, and returns.

`read_send_buffer` is the paired read side described above.

## Error Handling And Cleanup

The file consistently returns NTSTATUS values and logs with `ERR`, `WARN`, and `TRACE`. Common failures include allocation failure, malformed Btrfs items, unsupported compression/encryption/encoding, failed tree lookups, read/checksum failures, invalid handles, privilege failures, and readonly subvolume mutation detection.

The `send_thread` `end:` path releases kernel resources:

- Orphan list.
- Directory list and deleted child names.
- Thread handle.
- CCB send pointer.
- Send operation list entry.
- Send buffer.
- Clone array.
- Send counters.
- Context object.

One notable cleanup limitation: several mid-setup error paths in `send_subvol` free `context` and `data` but must be read carefully around clone allocation. Most clone validation failures free `clones`; the send buffer allocation failure path frees `context` but does not free `clones` if clone handles were accepted earlier, which is a potential leak candidate worth verifying against surrounding code revisions.

## Dependencies

This file depends heavily on Btrfs driver infrastructure from `btrfs_drv.h` and related modules:

- Tree lookup and traversal: `find_item`, `find_next_item`, `skip_to_difference`.
- CRC32C: `calc_crc32c`.
- Data IO/checksums: `read_data`, `load_csum`.
- Compression: `zlib_decompress`, `lzo_decompress`, `zstd_decompress`.
- Extent metadata helpers: `get_extent_data_len`, `get_extent_data_refcount`.
- FCB/subvolume helpers: `flush_subvol_fcbs`, `do_write`, `free_trees`.
- Windows kernel primitives: pool allocation, resources, events, system threads, object handles, privilege checks.

## Risks And Review Notes

- The file is correctness-sensitive because send streams must be replayable and path operations must be topologically valid.
- Buffer flushing temporarily releases `tree_lock`; the key revalidation is essential and should remain covered by tests.
- Path length fields are `uint16_t`, matching send TLV limits, but callers should be aware of possible truncation or overflow if very deep paths exceed send-stream limits.
- Extent handling has many arithmetic paths involving decoded size, logical offsets, compressed sizes, and file size truncation; boundary tests matter.
- Clone path reconstruction follows one inode ref path, not necessarily all possible hardlink paths.
- Malformed metadata mostly returns internal errors rather than trying to recover.
- Compressed regular extents are fully decompressed into memory before chunked output, which can be memory-heavy for large decoded extents.
- There is a probable allocation cleanup issue if `context->data` allocation fails after `clones` has been allocated.
