# File Research: sources/windows/reactos/drivers/filesystems/btrfs/fsctl.c

## Purpose

`fsctl.c` is the main file-system-control implementation for the ReactOS-imported WinBtrfs driver. It handles standard Windows `FSCTL_*` requests, Btrfs-specific ioctls, volume locking/dismount, sparse/zero/range/object-id operations, subvolume and snapshot creation, device add/resize/stat queries, xattrs, clone/duplicate extents, oplocks, retrieval pointers, and checksum reporting.

The file is the bridge between Windows IRP file-system-control dispatch and Btrfs metadata mutation. Most mutating paths validate caller access, readonly state, subvolume readonly state, acquire `tree_lock` and/or FCB resources, update in-memory metadata structures, mark FCBs/subvolumes dirty, and rely on existing transaction/write helpers such as `do_write`, `insert_tree_item`, `excise_extents`, `add_extent_to_fcb`, `update_dev_item`, and rollback lists.

## Main Entry Point

`fsctl_request(PDEVICE_OBJECT DeviceObject, PIRP* Pirp, uint32_t type)` dispatches control codes.

It first checks oplocks for file objects on filesystem VCBs, then switches on `type`. Implemented standard FSCTLs include:

- Oplock request/ack controls via `fsctl_oplock`.
- Volume lock/unlock/dismount/mounted/dirty queries.
- Compression query/set, with only `COMPRESSION_FORMAT_NONE` accepted.
- `FSCTL_FILESYSTEM_GET_STATISTICS`, returning a minimal NTFS-like stub to satisfy clients.
- `FSCTL_GET_RETRIEVAL_POINTERS`.
- `FSCTL_ALLOW_EXTENDED_DASD_IO`.
- `FSCTL_GET_OBJECT_ID` and `FSCTL_CREATE_OR_GET_OBJECT_ID`.
- Reparse point set/get/delete through helpers defined elsewhere.
- Sparse file, zero data, allocated ranges.
- Integrity get/set as stubs.
- `FSCTL_DUPLICATE_EXTENTS_TO_FILE`.

Implemented Btrfs private controls include file IDs, subvolume creation/snapshot, inode info get/set, device and usage reporting, balance/scrub delegation, add/remove/resize device, UUID query, stats reset, `mknod`, received-subvol marking, xattrs, readonly-subvol reservation, find/send/read-send-buffer, and checksum info.

Many unrelated Windows FSCTLs are intentionally stubbed with `STATUS_INVALID_DEVICE_REQUEST`.

## Subvolume and Snapshot Operations

`get_file_ids` returns subvolume id, inode number, and whether the file is the root-top file.

`get_uuid` generates 16 bytes using `KeQueryPerformanceCounter` and `RtlRandomEx`. It is used for subvolume and device UUID assignment.

`snapshot_tree_copy` copies a Btrfs tree block into a new metadata address for a snapshot. It reads the original node, allocates a new tree address, updates the tree header generation/tree id/fs uuid/address, increments references for file extents or child tree blocks, recalculates the checksum, writes the new block, waits for stripe writes, and returns the new address. It updates chunk used bytes and uses rollback support.

`flush_subvol_fcbs` flushes cache manager data for all open non-directory FCBs in a subvolume.

`do_create_snapshot` performs the actual snapshot transaction. It validates parent access, flushes source subvolume data and pending metadata, creates a new root, ensures the UUID root exists, assigns a unique subvolume UUID, inserts the UUID mapping, copies the source root tree, initializes the new `ROOT_ITEM`, optionally sets `BTRFS_SUBVOL_READONLY`, updates the original subvolume’s last snapshot generation, creates the visible directory entry/fileref in the target parent, updates parent inode times/size, clears uniqueness on source open extents, and writes the transaction. Rollback is used on failure.

`create_snapshot` validates the user buffer, supports 32-bit callers on 64-bit builds, converts the requested name from UTF-16 to UTF-8, validates name/collision, references the source subvolume handle, confirms it belongs to the same device and points at a subvolume root, clears uniqueness on open source extents, and calls `do_create_snapshot`.

`create_subvol` creates a new subvolume root. It validates parent directory, access, readonly states, and name, checks for collision, creates a root and UUID-root mapping, initializes root inode fields, creates a root FCB and `..` `INODE_REF`, assigns inherited security and compression/nodatacow state, creates the parent-visible fileref and directory child, updates parent inode/root metadata, and marks objects dirty. On failure, it marks partially created objects deleted or queues the new root for dropping.

`mark_subvol_dirty` queues dirty roots on `Vcb->dirty_subvols` and sets `Vcb->need_write`.

`recvd_subvol` sets received-subvolume metadata (`received_uuid`, send/receive transids, receive time) after `SE_MANAGE_VOLUME_PRIVILEGE`.

`reserve_subvol` lets a privileged process reserve a readonly subvolume for writes until the handle closes.

`find_subvol` finds a subvolume path by UUID or received UUID, optionally matching `ctransid`, using the UUID root and `get_subvol_path`.

## Inode, Extent, Sparse, and Clone Controls

`get_inode_info` reports Btrfs inode metadata, uid/gid/mode/rdev/flags, compression preference, inline/compressed/uncompressed/ZSTD/sparse byte accounting, and optionally number of disk extents.

`set_inode_info` changes inode flags, POSIX mode bits, uid, gid, and compression property. It checks access (`FILE_WRITE_ATTRIBUTES`, `WRITE_DAC`, `WRITE_OWNER`), disallows changing nodatacow on non-empty files, enforces nodatacow/compress exclusivity, updates derived nodatasum state, and marks the FCB dirty.

`set_sparse` toggles `FILE_ATTRIBUTE_SPARSE_FILE` for regular files and queues attribute notifications.

`zero_data` zeroes a byte range while preserving partial boundaries. It rewrites inline data, compressed extents, or normal extents as appropriate.

`set_zero_data` implements `FSCTL_SET_ZERO_DATA`. It validates ranges and write access, flushes cache, rejects streams/directories, handles inline extents, zeroes partial sector boundaries, excises full-sector ranges, purges cached pages, updates times/sequence/extents, and rolls back on failure.

`query_ranges` implements `FSCTL_QUERY_ALLOCATED_RANGES`. Non-sparse files report the full file as allocated. Sparse files coalesce non-ignored extents into allocated ranges and reports buffer overflow when needed.

`duplicate_extents` implements `FSCTL_DUPLICATE_EXTENTS_TO_FILE`. It validates source/destination handles, same volume, alignment for normal files, lock conflicts, access rights, non-overlap for same file, and compatible nodatasum flags. For streams, inline destinations, or inline sources, it falls back to buffered read/write. Otherwise it clones extent records, copies checksums, increments changed extent refs, excises destination extents, clears source `unique` flags, installs cloned extents, purges destination cache, and updates metadata/timestamps. It uses rollback on failure.

`fcb_is_inline` checks whether the first non-ignored extent is inline.

`get_retrieval_pointers` maps file extents to Windows VCN/LCN records. Holes and compressed extents report `Lcn = -1`; uncompressed extents use physical address plus extent offset.

`get_csum_info` reports file checksum type, checksum length, sector count, and per-sector checksum bytes. Sparse sectors are filled with the checksum of a zero sector; compressed extents receive dummy zero checksum bytes. Inline files report zero sectors.

`add_csum_sparse_extents` populates repeated sparse-sector checksums for CRC32C, XXHASH, SHA256, or BLAKE2.

## Device, Volume, and Filesystem State Operations

`get_devices` enumerates Vcb devices, including missing/readonly state, device/partition number, Btrfs size, physical max size, and device stats.

`get_usage` groups chunks by Btrfs block profile, totals logical size/used bytes, and calculates per-device allocation considering RAID0, RAID10, RAID5, and RAID6 profile factors.

`is_volume_mounted` checks removable devices with `IOCTL_STORAGE_CHECK_VERIFY`, updates media change counts, and returns verify-required status if media changed.

`flush_fcb_caches` flushes all open non-directory FCB cache sections.

`lock_volume` denies locking during scrub/balance, sends volume-lock notification, checks open children, flushes caches and metadata, and marks the VPB locked with the locking file object.

`do_unlock_volume` clears VPB lock state and resumes a paused balance if locking paused it.

`unlock_volume` validates the owner file object and sends volume-unlock notification.

`invalidate_volumes` requires `SE_TCB_PRIVILEGE`, references a file handle, finds matching VCBs by real device, marks removal, flushes writes, swaps VPBs when mounted, and uninitializes if no files are open.

`is_volume_dirty` returns a zero volume state only for the volume FCB.

`dismount_volume` denies pagefile/boot dismounts unless shutdown, sends dismount notification, flushes writes if unlocked, frees cached trees, marks removing, detaches the volume device extension, and uninitializes when no files remain.

`update_volumes` invalidates child volume generations after volume changes.

`allow_extended_dasd_io` enables DASD I/O on the volume FCB’s CCB.

`query_uuid` copies the filesystem UUID.

`reset_stats` requires manage-volume privilege, zeroes a device’s five Btrfs stat counters, marks stats dirty, and schedules a write.

`get_integrity_information` and `set_integrity_information` are stubs that validate buffers; get returns sector-sized checksum and cluster sizes with algorithm 0.

`fs_get_statistics` is a deliberate compatibility stub that returns a minimal `FILESYSTEM_STATISTICS` structure with NTFS type.

## Add and Resize Device

`is_device_part_of_mounted_btrfs_raid` reads a candidate device’s superblock, validates magic/checksum, compares filesystem and device UUIDs against mounted VCBs, and rejects adding a device that is already part of a mounted multi-device filesystem.

`trim_whole_device` issues whole-device DSM trim with `DEVICE_DSM_FLAG_ENTIRE_DATA_SET_RANGE`.

`add_device` requires manage-volume privilege, a PnP-backed writable VCB, a writable disk-like target, no existing mounted Btrfs RAID membership, and no partitions when adding a whole disk. It writes pending metadata, allocates and initializes a `device`, assigns a new device id and UUID, inserts a `DEV_ITEM` and device stats item, optionally trims the new device, zeroes the first MiB to hide old filesystem signatures, creates a `volume_child`, registers PnP notification, removes any drive letter, updates superblock device counts and total bytes, links the device into VCB state, writes metadata, and sends a volume size-change notification.

`resize_device` requires manage-volume privilege and sector-aligned size. It finds the device, rejects missing/readonly devices, handles shrink by either starting a balance over the truncated device range or directly updating device size when the tail is free, and handles growth by querying physical disk length and extending the free-space list. Successful resize updates `total_bytes`, marks `need_write`, and notifies volume size change.

## Xattrs, Security, and Special Node Creation

`mknod` implements Btrfs special node creation. It validates parent directory/access/name/type, optional privileged inode selection, UTF-8 conversion, collision checks, inherited POSIX mode/security/compression/nodatacow state, device `st_rdev` encoding, FCB/fileref creation, parent-child linkage, directory hash tables, parent inode updates, and notifications. A notable code-risk in this file: after selecting/generated `fcb->inode`, the function assigns `fcb->inode = inode`; `inode` came from the failed lookup path and may not be meaningful after `STATUS_OBJECT_NAME_NOT_FOUND`.

`check_inode_used` checks open FCB hash chains and then searches the subvolume tree for an existing `INODE_ITEM`.

`fsctl_get_xattrs` serializes non-empty xattrs into repeated `btrfs_set_xattr` records and terminates with a zero-length record.

`fsctl_set_xattr` handles both generic xattrs and several special names:
- `EA_NTACL`: privileged security descriptor update.
- `EA_DOSATTRIB`: Windows file attributes.
- `EA_REPARSE`: reparse xattr payload.
- `EA_EA`: Windows extended attributes, validated with `IoCheckEaBufferValidity`.
- `EA_CASE_SENSITIVE`: enables case sensitivity.
- `EA_PROP_COMPRESSION`: updates Btrfs compression property and inode compression flag.
- Rejects `user.*` because those are exposed as alternate streams.

The generic path replaces an existing xattr with the same name, marks it dirty, and marks the FCB dirty.

## Oplocks and Reparse/Object Helpers

`fsctl_oplock` validates file object, fileref, file/directory type, Windows 7 `FSCTL_REQUEST_OPLOCK` input/output buffers, directory shared-oplock limitations, checks file locks for shared oplock requests, rejects delete-pending batch/filter/handle caching requests, and delegates to `FsRtlOplockFsctrl`.

`get_object_id` synthesizes a Windows object id from inode and subvolume id and zeroes extended info.

Reparse point operations are dispatched from this file but implemented elsewhere.

## Concurrency and Error Handling

The file uses:
- `Vcb->tree_lock` for filesystem tree/metadata state.
- FCB header resources for per-file extent/inode/xattr state.
- `fileref_lock`, `dir_children_lock`, `dirty_subvols_lock`, `chunk_lock`, and VPB spin locks for narrower structures.
- Rollback lists for extent/tree mutations.
- Cache manager flush/purge before destructive or range-changing operations.
- Privilege checks for sensitive operations such as volume management, invalidation, xattr security injection, and explicit inode choice.

Most paths return NTSTATUS precisely and log failures with `ERR`/`WARN`.

## Research Notes

This file is core driver behavior, not simple glue. Its highest-risk areas are metadata mutation paths where Windows-visible semantics meet Btrfs copy-on-write state: snapshot/tree-copy refcounts, clone extents, xattr-backed Windows metadata, add/resize device, and volume dismount/lock. It also contains many compatibility stubs to make Windows callers tolerate unsupported NTFS-oriented controls.
