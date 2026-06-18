# File Research: sources/windows/winbtrfs/src/fsctl.c

## Purpose

`fsctl.c` is WinBtrfs' central filesystem-control dispatch and implementation file. It handles standard Windows FSCTLs, oplocks, volume lock/dismount flows, sparse/zero/range queries, object IDs, reparse-related delegation, and a large set of WinBtrfs private IOCTLs for subvolumes, snapshots, devices, balance/scrub control, xattrs, send/receive, resize, and checksum export.

## Main Entry Point

- `fsctl_request(PDEVICE_OBJECT DeviceObject, PIRP* Pirp, uint32_t type)`: dispatches FSCTL codes to local helpers or external subsystem functions.
- Performs an initial `FsRtlCheckOplock` for file-backed requests on filesystem VCBs.
- Uses `map_user_buffer()` for direct/output buffers where needed and updates `Irp->IoStatus.Information` for variable-length outputs.
- Unsupported Windows FSCTLs are deliberately stubbed with `STATUS_INVALID_DEVICE_REQUEST`; some are logged with `WARN`, while noisy `FSCTL_QUERY_VOLUME_CONTAINER_STATE` is only traced.

## Standard Windows FSCTL Behavior

Implemented or partially implemented:

- Oplocks: `fsctl_oplock()` validates file/directory cases, checks existing opens or file locks, rejects delete-pending handle oplocks, calls `FsRtlOplockFsctrl()`, and updates fast I/O state.
- Volume lifecycle: `lock_volume()`, `unlock_volume()`, `dismount_volume()`, `invalidate_volumes()`, `is_volume_mounted()`, `is_volume_dirty()`.
- Sparse/range operations: `set_sparse()`, `set_zero_data()`, `query_ranges()`.
- Retrieval pointers: `get_retrieval_pointers()` maps Btrfs extents and holes into Windows `RETRIEVAL_POINTERS_BUFFER`; compressed extents and holes report `LCN = -1`.
- Compression FSCTLs: `GET_COMPRESSION` reports `COMPRESSION_FORMAT_NONE`; `SET_COMPRESSION` only accepts `COMPRESSION_FORMAT_NONE`.
- Object IDs: `get_object_id()` synthesizes an object ID from inode and subvolume ID.
- Integrity: `get_integrity_information()` and `set_integrity_information()` are stubs that report sector-sized checksum/chunk sizes but do not enable Windows integrity streams.
- `FSCTL_FILESYSTEM_GET_STATISTICS` returns a minimal NTFS-like statistics block to avoid SMB breakage.

## WinBtrfs Private FSCTLs

Implemented private controls include:

- `FSCTL_BTRFS_GET_FILE_IDS`: returns subvolume ID, inode, and top-root flag.
- `FSCTL_BTRFS_CREATE_SUBVOL`: creates a new Btrfs root, root directory FCB, UUID tree entry, `..` inode ref, parent dir child, security descriptor, inherited mode/compression flags, and dirty markers.
- `FSCTL_BTRFS_CREATE_SNAPSHOT`: validates destination and source handles, flushes source data/metadata, creates a snapshot root, copies the source root tree block, updates extent references, links the snapshot into the destination directory, and marks source extents non-unique.
- `FSCTL_BTRFS_GET_INODE_INFO` / `SET_INODE_INFO`: exposes and mutates POSIX-like inode metadata, flags, ownership, mode, compression property, disk usage by compression type, sparse size, and extent count.
- `FSCTL_BTRFS_GET_DEVICES`: enumerates mounted/missing devices and device statistics.
- `FSCTL_BTRFS_GET_USAGE`: groups chunk usage by block group profile and reports per-device allocation.
- Balance/scrub control delegates to `start_balance`, `query_balance`, `pause_balance`, `resume_balance`, `stop_balance`, `start_scrub`, `query_scrub`, `pause_scrub`, `resume_scrub`, and `stop_scrub`.
- `FSCTL_BTRFS_ADD_DEVICE`: validates a target disk/partition, prevents adding an already-mounted Btrfs RAID member, checks writability and partition layout, creates `DEV_ITEM` and device stats items, clears the first MiB, registers PnP removal notification, removes drive letters, and updates superblock totals.
- `FSCTL_BTRFS_REMOVE_DEVICE`: delegated to `remove_device()`.
- `FSCTL_BTRFS_RESET_STATS`: zeroes in-memory per-device error counters and marks stats dirty.
- `FSCTL_BTRFS_MKNOD`: creates Unix-style file types including directories, regular files, symlinks, FIFOs, sockets, char devices, and block devices.
- `FSCTL_BTRFS_RECEIVED_SUBVOL`: records received-subvolume UUID/generation metadata for send/receive.
- `FSCTL_BTRFS_GET_XATTRS` / `SET_XATTR`: enumerates and mutates Btrfs xattrs, including special handling for NT security descriptors, DOS attributes, reparse xattr, Windows EAs, case-sensitive flag, and compression property.
- `FSCTL_BTRFS_RESERVE_SUBVOL`: privileged reservation of a readonly subvolume for write access by the current process.
- `FSCTL_BTRFS_FIND_SUBVOL`: resolves subvolume UUID or received UUID plus optional creation transaction ID to a path.
- `FSCTL_BTRFS_SEND_SUBVOL` / `READ_SEND_BUFFER`: delegated send-stream path.
- `FSCTL_BTRFS_RESIZE`: extends or shrinks a device; shrink can trigger a balance over the truncated range.
- `FSCTL_BTRFS_GET_CSUM_INFO`: exports checksum type, checksum length, sector count, and per-sector checksums, synthesizing sparse-sector checksums and using zero placeholders for compressed extents.

## Key Internal Helpers

- `snapshot_tree_copy()`: reads a tree block, allocates a new metadata address, rewrites header fields, increments data or child tree-block references, recalculates checksum, and writes the cloned block.
- `flush_subvol_fcbs()` / `flush_fcb_caches()`: flush cache manager state for open FCBs before snapshot, lock, invalidate, or dismount operations.
- `zero_data()`: rewrites partial ranges for inline, compressed, or regular extent layouts; used by `set_zero_data()` for unaligned boundaries.
- `duplicate_extents()`: implements reflink/clone semantics. It copies data for ADS, inline, compressed-inline, or unaligned cases; otherwise creates shared extent records, copies checksums, updates extent refs, excises destination ranges, and purges cached destination pages.
- `mark_subvol_dirty()`: adds roots to `dirty_subvols` and sets `Vcb->need_write`.
- `get_csum_info()` and `add_csum_sparse_extents()`: package checksum data for callers across CRC32C, xxhash, SHA256, and BLAKE2 checksum sizes.

## Locking and State Discipline

- `Vcb->tree_lock` guards most metadata mutations and global filesystem state.
- FCB resource locks guard inode/extents/xattrs per file.
- `fileref_lock`, `dir_children_lock`, `dirty_subvols_lock`, `chunk_lock`, and global loading locks are used for narrower state.
- Rollback lists are used for snapshot, zeroing, and clone paths that touch extent/tree metadata.
- Volume lock/dismount paths flush cache manager state, write dirty metadata, free cached trees, and update VPB state under the VPB spin lock.

## Dependencies

- Driver core structures and helpers from `btrfs_drv.h`.
- Public/private IOCTL definitions from `btrfsioctl.h`.
- Checksum support via `crc32c.h` and general checksum helpers.
- Windows kernel APIs: `FsRtl*`, `Cc*`, `Io*`, `Se*`, VPB manipulation, mount manager/device IOCTLs.
- Cross-file subsystem functions: balance, scrub, send, remove-device, reparse point helpers, tree insertion/deletion, extent ref updates, security descriptor helpers, cache/read/write helpers.

## Research Notes

- This is a high-blast-radius file: user-mode IOCTL inputs directly drive metadata mutation, device topology changes, and subvolume operations.
- Many handlers include explicit privilege checks, readonly/subvolume-readonly checks, user-mode access checks, and 32-bit process handle handling.
- Snapshot and clone paths carefully clear extent uniqueness because shared extents may now be referenced by multiple files/subvolumes.
- Several Windows FSCTLs are intentionally stubs; compatibility behavior is selective rather than full NTFS emulation.
- `mknod()` deserves focused review: after computing or validating the desired inode, the code assigns `fcb->inode = inode`, where `inode` is the lookup output from `find_file_in_dir()` after a not-found result. That looks potentially fragile and may be a real bug depending on surrounding helper semantics.
