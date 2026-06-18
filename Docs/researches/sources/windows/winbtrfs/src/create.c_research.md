# File Research: sources/windows/winbtrfs/src/create.c

## Scope

This file implements WinBtrfs `IRP_MJ_CREATE` handling and the supporting object-open/create machinery. It covers FCB and file-reference allocation, path parsing, directory child lookup and caching, inode/xattr/extent loading, named stream handling, new inode creation, existing-file open semantics, reparse handling, oplock handoff, open-by-file-id support, removable-media verification, and volume-open handling.

The file is tightly coupled to Windows filesystem driver conventions (`FILE_OBJECT`, `IRP`, share access, security descriptors, oplocks, VPB state, ECPs) and to WinBtrfs in-memory objects (`device_extension`, `root`, `fcb`, `file_ref`, `dir_child`, `extent`, `xattr`).

## Entry Points And Major APIs

- `create_fcb(Vcb, pool_type)`: allocates and initializes an FCB, its nonpaged companion, advanced FSRTL header, resources, file lock, oplock, extent/hardlink/xattr lists, and directory child indexes.
- `create_fileref(Vcb)`: allocates a `file_ref`, initializes its reference count and children list.
- `find_file_in_dir(filename, fcb, subvol, inode, pdc, case_sensitive)`: searches a loaded directory's hash-indexed `dir_child` cache, using either exact Unicode hashes or upcased hashes.
- `split_path(Vcb, path, parts, stream)`: splits a Unicode path into `name_bit` components, handles trailing separators, detects alternate data stream syntax, and removes a `:$DATA` suffix from stream names.
- `load_csum(Vcb, csum, start, length, Irp)`: reads checksum-tree `TYPE_EXTENT_CSUM` items into a caller buffer for a sector range.
- `load_dir_children(Vcb, fcb, ignore_size, Irp)`: populates a directory FCB's child lists from `TYPE_DIR_INDEX` items and optionally synthesizes the `$Root` entry.
- `open_fcb(Vcb, subvol, inode, type, utf8, always_add_hl, parent, pfcb, pooltype, Irp)`: opens or loads an inode into an FCB, including inode item, hardlinks, xattrs, streams, extents, attributes, security, directory children, allocation sizes, and global FCB indexing.
- `open_fcb_stream(Vcb, dc, parent, pfcb, Irp)`: opens a named stream stored as a `user.<stream>` xattr on the parent file.
- `open_fileref_child(...)`: resolves one path component below a parent `file_ref`, including normal children, subvolume root entries, dummy inaccessible roots, and alternate data stream children.
- `open_fileref(...)`: resolves full or relative paths into a `file_ref`, optionally returning the parent, parsed length for reparses, and filename offsets.
- `add_dir_child(...)`: adds a new in-memory `dir_child` to a directory's index and hash lists.
- `inherit_mode(parfcb, is_dir)`: derives POSIX mode bits for a new child from the parent, clearing sticky/setuid and non-directory setgid as needed.
- `file_create_parse_ea(fcb, ea)`: normalizes create-time EA buffers, consumes LXSS metadata EAs (`LXUID`, `LXGID`, `LXMOD`, `LXDEV`), and stores remaining EAs in the `EA` xattr format.
- `file_create2(...)`: creates a normal file or directory inode and file reference below a parent directory.
- `create_stream(...)`: creates an alternate data stream as a `user.<stream>` xattr-backed ADS FCB and directory-child entry with index `0`.
- `file_create(...)`: high-level create path for missing names, including ECP handling, stream splitting, parent access checks, EA validation, share access setup, CCB allocation, atomic-create reparse/case-sensitive flags, and notifications.
- `get_reparse_block(fcb, data)`: returns reparse data for file/symlink/directory reparse points; symlink targets are converted from stored UTF-8 Btrfs symlink data into an `IO_REPARSE_TAG_SYMLINK` buffer.
- `fcb_load_csums(Vcb, fcb, Irp)`: lazily loads checksums for regular data extents into each extent's `csum` buffer.
- `open_file3(...)`: finalizes an existing-file open after access/share/oplock checks, handling overwrite/supersede truncation, EA replacement/removal, stream removal, notifications, CCB setup, paging-file extent normalization, and open counters.
- `oplock_complete(Context, Irp)`: asynchronous oplock completion callback that resumes `open_file3`, updates access state, loads checksums, completes the IRP, and signals the waiter.
- `open_file2(...)`: validates access and disposition for an existing `file_ref`, handles readonly/delete restrictions, reparses, directory-vs-file options, share access, oplock checks, and calls `open_file3`.
- `open_fileref_by_inode(Vcb, subvol, inode, pfr, Irp)`: resolves an inode number to a usable `file_ref`, reconstructing a parent/name from hardlink refs, inode refs, extrefs, or root backrefs.
- `open_file(DeviceObject, Vcb, Irp, rollback, opctx)`: dispatches by requested disposition and options, resolves names or file IDs, handles missing vs existing objects, invokes create/open logic, and sets cache support.
- `verify_vcb(Vcb, Irp)`: checks removable backing devices with `IOCTL_STORAGE_CHECK_VERIFY` and invokes `IoVerifyVolume` when media change is detected.
- `has_manage_volume_privilege(access_state, processor_mode)`: checks `SE_MANAGE_VOLUME_PRIVILEGE` for volume opens.
- `drv_create(DeviceObject, Irp)`: exported `IRP_MJ_CREATE` dispatch routine for filesystem, volume, and master device opens.

## Core Control Flow

The main create path begins in `drv_create`. It enters the filesystem, sets top-level IRP state, handles the master device object as a simple open, delegates volume device objects to `vol_create`, rejects unmounted/removing volumes, verifies removable media, and acquires `Vcb->load_lock`. Empty-name opens without a related file object are treated as volume opens and create a CCB attached to `Vcb->volume_fcb`.

Normal file opens acquire `Vcb->tree_lock` shared unless already held, then `Vcb->fileref_lock` shared, and call `open_file`. `open_file` decodes create disposition and option bits, handles `FILE_OPEN_BY_FILE_ID`, resolves paths through `open_fileref`, processes reparse returns, detects deleted references, and chooses either existing-file open (`open_file2`) or missing-file create (`file_create`). A rollback list is passed through mutating operations and is either cleared on success or rolled back by `drv_create` on failure.

Path resolution is layered. `open_fileref` normalizes absolute paths, handles related opens, splits components with `split_path`, optionally removes the final component when the caller wants the parent, then repeatedly calls `open_fileref_child`. `open_fileref_child` uses a directory's cached `dir_child` entries to open child FCBs, attaches new `file_ref` objects to parent child lists, honors case sensitivity from the relevant directory, and stops with `STATUS_REPARSE` if an intermediate component is a reparse point.

FCB loading in `open_fcb` first looks for an existing non-ADS FCB in the subvolume hash buckets. If absent, it loads the inode item, guesses Btrfs type from POSIX mode if needed, scans following tree items for hardlinks, xattrs, and extent data, loads directory children for directories, computes file sizes/allocation sizes, derives attributes and security descriptors, and inserts the FCB into sorted per-subvolume/global FCB lists. Xattr handling recognizes WinBtrfs metadata xattrs for reparse data, EAs, DOS attributes, NT security descriptors, compression property, case sensitivity, and user xattrs used to represent named streams.

Creation of a normal file or directory is handled by `file_create2`. It converts the final Unicode name to UTF-8, updates parent directory timestamps and size, allocates a new inode number from `subvol->lastinode`, initializes POSIX mode, Btrfs inode flags, compression property, Windows attributes, security descriptor, create-time EAs, optional preallocation, and directory child caches for new directories. It then double-checks for a concurrent child with the same name under the parent directory lock, inserts a `dir_child`, links a `file_ref`, marks FCBs and refs dirty, updates subvolume root item time, and queues notifications.

Named stream creation in `create_stream` first opens or creates the base file, rejects reserved stream names (`DOSATTRIB`, `EA`, `reparse`, `casesensitive`), enforces parent write access and readonly rules, creates an ADS FCB backed by a `user.<stream>` xattr, checks the leaf size budget for the xattr item, links the ADS FCB after the parent FCB, inserts an index-0 `dir_child`, marks the stream dirty, updates parent times, and sends stream-name notifications.

Existing-file opens go through `open_file2` and `open_file3`. `open_file2` checks supersede/overwrite legality, security access, delete-pending ancestors, readonly restrictions, Btrfs verity readonly state, reparse behavior, directory/file option mismatches, share access, and oplocks. If an oplock break is pending, it returns `STATUS_PENDING` with an `oplock_context`; `drv_create` waits for completion before returning. `open_file3` performs truncation and attribute/EA updates for overwrite-style dispositions, removes existing streams on full overwrite of a non-ADS file, emits notifications, creates a CCB, sets `FILE_OBJECT` contexts and section object pointer, updates create information, and normalizes paging-file extents from prealloc to regular.

## Important State Mutated

- `fcb`: reference count, inode metadata, type, Btrfs inode flags, Windows attributes, security descriptor, EA/reparse/compression/case-sensitive xattrs, extents, hardlinks, directory children, ADS fields, dirty flags, share access, open count, file sizes, cache support, paging-file flags.
- `file_ref`: reference/open counts, parent/child links, associated `dir_child`, created/deleted flags, dirty-list state, delete-on-close traversal.
- `dir_child`: Btrfs key, index, type, UTF-8/UTF-16 names, case-folded name, hash values, stream entries, `fileref` backpointers, synthetic `$Root` marker.
- `root`: FCB hash buckets, `fcbs_version`, `lastinode`, root item transaction/change times, parent/subvolume relationships.
- `device_extension`: open file count, loaded roots, root fileref, dummy/volume FCBs, global FCB list, locks, volume mounted/removing/readonly state, options, superblock generation and sizes.
- `IRP` / `FILE_OBJECT`: `IoStatus.Information`, `Tail.Overlay.AuxiliaryBuffer` for reparses, `FsContext`, `FsContext2`, `SectionObjectPointer`, `Vpb`, cache flags, granted access bookkeeping.

## Dependencies

Windows kernel/IFS APIs used include `FsRtlEnterFileSystem`, `FsRtlSetupAdvancedHeader`, `FsRtlInitializeFileLock`, `FsRtlInitializeOplock`, `FsRtlCheckOplock`, `FsRtlAreNamesEqual`, `FsRtlDoesNameContainWildCards`, `FsRtlValidateReparsePointBuffer`, `IoSetShareAccess`, `IoCheckShareAccess`, `IoUpdateShareAccess`, `IoRemoveShareAccess`, `IoCompleteRequest`, `IoVerifyVolume`, `MmCanFileBeTruncated`, `MmFlushImageSection`, `SeAccessCheck`, `SePrivilegeCheck`, `SeLockSubjectContext`, `IoCheckEaBufferValidity`, `RtlUpcaseUnicodeString`, `RtlUpperString`, resource locks, lookaside lists, pool allocation, and removable storage IOCTLs.

Project-local dependencies include tree traversal and mutation (`find_item`, `find_next_item`), name conversion (`utf8_to_utf16`, `utf16_to_utf8`), hashing (`calc_crc32c`), xattr retrieval (`get_xattr`), attribute/security helpers (`get_file_attributes`, `get_file_attributes_from_xattr`, `fcb_get_sd`, `fcb_get_new_sd`, `set_reparse_point2`), file extent operations (`read_file`, `extend_file`, `truncate_file`, `stream_set_end_of_file_information`), object lifetime (`free_fcb`, `reap_fcb`, `free_fileref`, `reap_fileref`, `increase_fileref_refcount`), dirty marking and notifications (`mark_fcb_dirty`, `mark_fileref_dirty`, `send_notification_fileref`, `queue_notification_fcb`), rollback (`do_rollback`, `clear_rollback`), and subvolume helpers (`find_default_subvol`, `is_subvol_readonly`, `make_file_id`).

## Notable Behaviors

- Directory caches are indexed three ways: insertion/index order, case-sensitive hash, and uppercase case-insensitive hash. `hash_ptrs` and `hash_ptrs_uc` provide 256 bucket entry points keyed by the high byte of CRC32C.
- `open_fileref` supports Win32 ADS syntax by splitting the base file and stream component; streams are represented as xattrs and are exposed as index-0 children before normal directory entries.
- Synthetic `$Root` exposure allows access to the filesystem tree root when the mounted default subvolume is not `BTRFS_ROOT_FSTREE`, unless `options.no_root_dir` disables it.
- A dummy FCB is used for subvolume roots that should be hidden/inaccessible from the current parent relationship.
- `open_fileref_by_inode` reconstructs a path by following hardlinks or inode refs and then opening the parent recursively. Subvolume roots require root backref handling or the synthetic `$Root` path.
- Reparse handling deliberately returns the reparse tag in `IoStatus.Information` and stores a reparse buffer in `Irp->Tail.Overlay.AuxiliaryBuffer` so the I/O manager can process symlinks/reparse points.
- Atomic create ECP support is partial: reparse-point setting and case-sensitive-directory flags are honored, while query-on-create and create-redirection ECPs are logged as unhandled.
- LXSS callers are detected on AMD64 by checking whether the process basic information has a NULL PEB; this affects CCB state and reparse tags elsewhere.
- Create-time LXSS EAs can change the new FCB's UID, GID, POSIX mode, device number, and even Btrfs file type for non-directory special files.

## Risks And Edge Cases

- In `create_stream`, the `existing_dc` collision path returns without releasing `parfileref->fcb->nonpaged->dir_children_lock`. It also assumes `existing_dc->fileref` is non-NULL before incrementing it, which may not hold for a loaded stream directory child that has not yet been opened.
- The case-insensitive duplicate check in `file_create2` computes an uppercase hash but compares `dc->name.Length` and `dc->name.Buffer` to the uppercase buffer rather than `dc->name_uc`; this can miss or mishandle case-insensitive collisions.
- `load_dir_children` allocates `hash_ptrs` before `hash_ptrs_uc`; if the second allocation fails, the first allocation is not freed in this function.
- Several error exits during create roll back selected parent size changes manually, but broad correctness relies on the caller's rollback list and object cleanup. Some partially linked objects may already be visible in memory before an error path.
- `file_create2` adjusts parent directory size before many later allocations and access checks complete; most failures subtract it back, but this pattern is fragile.
- `open_file2` treats failure to build a reparse block as non-fatal and proceeds with a normal open by setting `Status = STATUS_SUCCESS`; malformed reparse metadata can therefore degrade into opening the reparse file itself.
- `get_reparse_block` for symlinks allocates based on UTF-16 conversion length, then calls `utf8_to_utf16` using `size` rather than the actual `bytes_read`; if `read_file` returns fewer bytes than the capped size, this depends on the read helper's behavior.
- `open_fileref_by_inode` recursively opens parents and can traverse complex hardlink/subvolume relationships; corrupted or cyclic metadata would stress this path.
- The code uses CRC32C hashes for lookup acceleration but usually follows with full name comparisons. ADS FCB lookup has a FIXME for xattr hash collisions.
- `drv_create` waits synchronously for pending oplock completion after initially not completing the IRP. This keeps dispatch return simple, but long oplock delays tie up the create caller.

## Summary

`create.c` is the WinBtrfs namespace and open/create hub. It bridges Windows create semantics with Btrfs roots, inodes, directory indexes, xattrs, extents, subvolumes, named streams, reparse points, share access, security, and oplocks. Most later filesystem operations depend on the FCB/file-ref/CCB state built here.
