# File Research: sources/windows/winbtrfs/src/fileinfo.c

## Purpose

Implements WinBtrfs handling for Windows file information and extended attribute IRPs. This file is the bridge between Windows `FileInformationClass` operations and WinBtrfs in-memory Btrfs objects: `fcb`, `ccb`, `file_ref`, `dir_child`, `root`, `INODE_ITEM`, xattrs, alternate data streams, hardlinks, and subvolumes.

It handles metadata mutation, rename/link/disposition semantics, file-size changes, information queries, hardlink/stream enumeration, Linux/WSL metadata exposure, and EA query/set operations.

## Main Responsibilities

- Dispatch `IRP_MJ_SET_INFORMATION` through `drv_set_information`.
- Dispatch `IRP_MJ_QUERY_INFORMATION` through `drv_query_information`.
- Dispatch `IRP_MJ_QUERY_EA` and `IRP_MJ_SET_EA`.
- Set basic metadata: timestamps, attributes, readonly subvolume flags, change notifications.
- Set delete disposition, including Windows disposition-ex flags and POSIX delete semantics.
- Rename files, directories, subvolume roots, hardlinks, and alternate data streams.
- Create hardlinks and maintain `hardlink` side lists.
- Resize normal files and ADS-backed streams.
- Maintain directory child index/hash lists during renames and moves.
- Move file-reference subtrees across subvolumes by duplicating/retargeting FCBs and filerefs.
- Fill Windows query structures for basic, standard, internal, EA, name, stream, link, ID, stat, LX stat, case-sensitive, compression, and network-open information.
- Store and enumerate EAs using `FILE_FULL_EA_INFORMATION` serialized into `fcb->ea_xattr`.
- Interpret special LXSS EA names for UID, GID, and mode updates.

## Dispatch Entry Points

- `drv_set_information`: Validates filesystem state, mount state, readonly state, CCB/FCB presence, access masks, oplocks, and subvolume readonly rules before routing set operations.
- `drv_query_information`: Validates device type and delegates to `query_info`, then completes the IRP.
- `drv_query_ea`: Maps the output buffer, validates access, optionally redirects ADS queries to the parent file, and returns selected or enumerated EAs.
- `drv_set_ea`: Validates the EA buffer, updates serialized EA storage, handles LXSS metadata EAs, marks the inode dirty, and sends EA notifications.

## Set-Information Paths

- `set_basic_information` updates creation/access/write/change times, DOS attributes, readonly subvolume state, root item timestamps, inode generation/sequence, and file notifications.
- `set_disposition_information` toggles `delete_on_close`, enforces readonly/root/non-empty-directory/image-section checks, and supports disposition-ex flags including POSIX semantics.
- `set_rename_information` is the central rename implementation. It handles destination parsing, replacement checks, access checks, POSIX replacement, same-directory renames, cross-directory moves, cross-subvolume moves, ADS-to-file conversion, and file-to-ADS conversion.
- `set_link_information` creates hardlinks after checking directory/ADS restrictions, link count limits, destination replacement policy, subvolume boundary rules, and parent permissions.
- `set_end_of_file_information` truncates or extends normal files through `truncate_file`/`extend_file`, handles ADS length changes through `stream_set_end_of_file_information`, updates cache-manager file sizes, and queues notifications.
- `set_allocation_information` adjusts sector-aligned allocation size, using truncation/extension helpers and cache-manager size updates.
- `set_valid_data_length_information` validates VDL constraints and updates cache sizes; the comment notes the filesystem already effectively treats VDL as max.
- `set_position_information` only updates `FileObject->CurrentByteOffset`.
- `set_case_sensitive_information` toggles the per-directory case-sensitive flag and marks the FCB dirty.

## Rename and Move Support

- `has_open_children` recursively blocks rename/replacement paths that would affect open descendants.
- `duplicate_fcb` deep-copies an FCB’s inode item, security descriptor, extents, checksums, hardlinks, reparse/EA xattrs, compression properties, ADS buffers, and generic xattrs for dummy/deleted shadow objects.
- `add_children_to_move_list` recursively opens directory children and builds a `move_entry` tree for cross-subvolume moves.
- `move_across_subvols` performs the heavy cross-subvolume move path:
  - builds a recursive move list,
  - creates dummy FCBs and filerefs for old locations,
  - assigns new inode numbers in the destination subvolume,
  - updates extent reference staging for regular/preallocated extents,
  - handles subvolume-root parent changes,
  - rewires child/parent fileref lists,
  - updates directory child indexes and hash lists,
  - adjusts parent directory sizes and root item timestamps,
  - marks affected FCBs/filerefs dirty,
  - sends removal/addition/parent-modified notifications.
- `rename_stream`, `rename_stream_to_file`, and `rename_file_to_stream` implement WinBtrfs ADS semantics on top of Btrfs user xattrs. They translate stream names into `user.` xattr names, reserve driver-private xattr names, enforce xattr-size limits, and create dummy deleted xattr records for flush-time cleanup.
- `insert_dir_child_into_hash_lists` and `remove_dir_child_from_hash_lists` keep case-sensitive and uppercased CRC32C directory-child hash lists ordered and maintain the 256-entry bucket pointer accelerators.

## Query-Information Paths

- `query_info` routes `FileInformationClass` values and sets `IoStatus.Information` based on remaining buffer length.
- `fill_in_file_basic_information` returns timestamps and attributes, using parent metadata for ADS.
- `fill_in_file_network_open_information` returns timestamps, allocation size, EOF, and attributes.
- `fill_in_file_standard_information` returns allocation size, EOF, link count, directory flag, and delete-pending state.
- `fill_in_file_internal_information` returns the packed WinBtrfs file ID via `make_file_id`.
- `fill_in_file_ea_information` returns the NT-style EA size value stored in `fcb->ealen`.
- `fileref_get_filename` constructs full names by walking parent filerefs and prepending `\` for normal components or `:` for streams.
- `fill_in_file_name_information` returns normalized/name information and appends `:$DATA` for ADS.
- `fill_in_file_attribute_information` returns attributes and reparse tags.
- `fill_in_file_stream_information` enumerates the default unnamed stream and ADS entries represented as directory children with index `0`.
- `fill_in_hard_link_information` and `fill_in_hard_link_full_id_information` enumerate link entries, resolving parent filerefs by inode and falling back to stored hardlink names when needed.
- `fill_in_file_id_information` returns a 128-bit ID composed from inode and subvolume ID, plus a volume serial from the superblock UUID.
- `fill_in_file_stat_information` and `fill_in_file_stat_lx_information` expose newer Windows stat structures, including WSL/LX UID, GID, mode, device IDs, case sensitivity, and special reparse tags for socket/FIFO/char/block device types.
- `fill_in_file_case_sensitive_information` reports the directory case-sensitive flag.
- `fill_in_file_compression_information` reports compressed-file-size fields using logical size for non-directories and ADS data length for streams.

## EA Handling

- `drv_query_ea` supports both named EA lookup lists and sequential/indexed enumeration.
- EA names are uppercased before comparison, matching the file’s serialized EA records case-insensitively.
- Query paths honor `SL_RETURN_SINGLE_ENTRY`, `SL_INDEX_SPECIFIED`, and `SL_RESTART_SCAN`, using `ccb->ea_index` for scan continuation.
- `drv_set_ea` first converts current serialized EAs into temporary `ea_item` entries, applies incoming changes, removes zero-length values, then serializes the remaining entries back into `fcb->ea_xattr`.
- `drv_set_ea` treats `lxuid`, `lxgid`, and `lxmod` as Linux metadata updates rather than ordinary persistent EA entries.
- EA mutation updates inode generation/sequence/ctime, marks EA and inode state dirty, and queues `FILE_NOTIFY_CHANGE_EA`.

## Windows Compatibility Definitions

For non-MSVC builds, this file defines newer Windows information classes and structures not always present in MinGW headers, including:

- `FileIdInformation`
- `FileHardLinkFullIdInformation`
- `FileDispositionInformationEx`
- `FileRenameInformationEx`
- `FileStatInformation`
- `FileStatLxInformation`
- `FileCaseSensitiveInformation`
- `FileLinkInformationEx`
- `FileStorageReserveIdInformation`

It also defines related rename, disposition, link, LX metadata, and case-sensitive constants.

## Locking and State Discipline

- Set rename/link paths take `Vcb->tree_lock` shared, `Vcb->fileref_lock` exclusive, and the target FCB resource exclusive.
- Size-changing paths take `Vcb->tree_lock` shared and the FCB resource exclusive.
- Directory child list/hash mutations use `fcb->nonpaged->dir_children_lock`.
- FCB subvolume list mutations use the global FCB lock through `acquire_fcb_lock_exclusive`.
- Query paths use lighter locking where needed, especially for hardlink enumeration and directory stream enumeration.
- Rollback lists are used for rename, link, truncation, extension, and conversion paths; successful operations call `clear_rollback`, failures call `do_rollback`.

## Cross-File Interactions

- Uses core structures and helpers from `btrfs_drv.h`.
- Uses CRC32C helpers from `crc32c.h` for inode hashes, dir-child hashes, and ADS xattr hashes.
- Calls tree/data mutation helpers such as `truncate_file`, `extend_file`, `excise_extents`, `add_extent_to_fcb`, `do_write_file`, and `update_changed_extent_ref`.
- Calls fileref helpers such as `open_fileref`, `open_fileref_child`, `open_fileref_by_inode`, `create_fileref`, `delete_fileref`, `free_fileref`, and `mark_fileref_dirty`.
- Calls FCB helpers such as `create_fcb`, `free_fcb`, `reap_fcb`, `mark_fcb_dirty`, `fcb_alloc_size`, and `fast_io_possible`.
- Uses Windows kernel/cache/security APIs including `FsRtlCheckOplock`, `CcFlushCache`, `CcSetFileSizes`, `MmCanFileBeTruncated`, `MmFlushImageSection`, `SeAccessCheck`, `SeAssignSecurity`, `IoCheckEaBufferValidity`, and file notification APIs.

## Important Behavior

- ADS are represented as Btrfs xattrs and appear as directory children with stream syntax in Windows queries.
- Stream-to-file and file-to-stream renames physically transform FCB/fileref state rather than just changing names.
- Subvolume root handling is special: root deletion/rename is blocked for `\$Root`, readonly flags live in the root item, and moving a subvolume root updates parent subvolume IDs.
- Directory sizes are updated using twice the UTF-8 name length, matching the driver’s directory accounting convention.
- File IDs combine inode and subvolume ID, which is critical because Btrfs inode numbers are only unique within a subvolume.
- Query stat paths map Btrfs UNIX object types to Windows reparse tags for WSL-visible special files.
- Readonly volume/subvolume checks are centralized in dispatch, with specific exceptions for position updates and selected subvolume-root metadata operations.
- Replacement rename/link paths enforce open-child/open-target restrictions unless POSIX semantics are requested.
- Cache-manager file sizes are updated after successful size changes and protected with exception handling.

## Edge Cases and Risks

- The file contains several `FIXME` notes around subvolume deletion checks, paging-file FCB duplication, cleanup of dummy move objects, POSIX stream overwrite behavior, checksum handling for ADS-to-file conversion, dummy fileref creation, non-buffered alignment for file position, link input length validation, ignoring `RootDirectory`, fileref filename locking, and accessible-link counts.
- Some complex rename/conversion paths mutate many linked structures before all later allocations and operations have completed; rollback exists, but these paths are high risk because they combine FCB lists, fileref lists, dir-child indexes, xattrs, extents, and notifications.
- Cross-subvolume moves update extent references for regular/preallocated extents; failures after partial staging depend on rollback and dirty-state handling in other modules.
- `create_directory_fcb` can return after hash-pointer allocation failure without visibly freeing all earlier allocations in this function.
- `stream_set_end_of_file_information` calls `ExFreePool(data)` when allocation fails even though `data` is `NULL`; this is probably harmless on Windows pool free semantics but is odd.
- `set_link_information` logs `add_dir_child` failure but continues to dereference/use `dc`, so failure handling there is fragile.
- Hardlink full-ID enumeration assumes child filerefs have `dc` in one loop branch, whereas the non-full version checks `fr2->dc`; malformed or transitional fileref state could matter.
- `query_info` fills `FileAllInformation` progressively and does not check every helper return, relying heavily on the final length accounting.
- Multiple paths depend on CCB access masks and requestor mode checks; kernel-mode callers bypass several user-mode permission checks.
- Newer Windows information classes are partially supported; `FileStorageReserveIdInformation` is explicitly unimplemented and `FileRemoteProtocolInformation` returns invalid parameter.

## Research Summary

`fileinfo.c` is a major WinBtrfs integration file for Windows metadata semantics. It translates Windows file-information IRPs into Btrfs inode, subvolume, fileref, hardlink, stream, xattr, and cache-manager state changes. The most intricate code is rename/link handling, especially cross-subvolume moves and alternate-data-stream conversions. Query handling is broad and exposes both traditional Windows metadata and newer WSL/LX stat details. The file is central to correctness for namespace operations, size changes, metadata updates, EA behavior, and user-visible file identity.
