# File Research: sources/windows/reactos/drivers/filesystems/btrfs/fileinfo.c

## Scope

This report covers the complete `fileinfo.c` file in the ReactOS-imported WinBtrfs filesystem driver. The file implements Windows file information, extended attribute, rename, link, disposition, size, stream, and stat query/set behavior for Btrfs FCBs and file references. It is a major metadata mutation module: beyond `IRP_MJ_QUERY_INFORMATION` and `IRP_MJ_SET_INFORMATION`, it owns alternate data stream rename/conversion logic, hardlink creation and enumeration, cross-subvolume move emulation, directory child hash maintenance, EA storage, LX metadata EAs, and notification emission for these operations.

## Primary Responsibilities

- Provides compatibility definitions for Windows 10 file information classes and structures when building with MinGW or ReactOS headers.
- Implements `drv_set_information()` for allocation, basic attributes/times, disposition/delete-on-close, EOF/valid-data-length, file position, rename, hardlink, and selected extended Windows information classes.
- Implements `drv_query_information()` and `query_info()` for basic, standard, internal, EA, name, stream, network-open, compression, hardlink, ID, stat, LX stat, and case-sensitive information classes.
- Implements `drv_query_ea()` and `drv_set_ea()` for NT extended attributes stored in the driver xattr buffer, including special handling for LXSS UID/GID/mode metadata.
- Maintains directory child ordered/hash lists through `insert_dir_child_into_hash_lists()` and `remove_dir_child_from_hash_lists()`.
- Handles file and stream rename transformations, including stream-to-file and file-to-stream conversion where Win32 stream names are represented as Btrfs xattrs.
- Handles cross-subvolume moves by duplicating FCB/file-reference state, assigning new inode numbers, updating extent references, and leaving deleted dummy records behind for flush/rollback consistency.
- Updates inode/root generation, sequence, timestamps, link counts, parent directory sizes, dirty flags, rollback records, cache-manager sizes, and filesystem notifications after metadata changes.

## Set Information Dispatch

`drv_set_information()` validates the target device, mount state, readonly volume state, FCB/CCB presence, and readonly subvolume restrictions before dispatching by `FileInformationClass`. It enters the filesystem, establishes top-level IRP state, checks oplocks, sets `IoStatus.Information` to zero, and completes the IRP before returning.

Supported set paths include:
- `FileAllocationInformation` maps to `set_end_of_file_information(..., prealloc=true)`.
- `FileBasicInformation` maps to `set_basic_information()` after `FILE_WRITE_ATTRIBUTES` access checks.
- `FileDispositionInformation` and non-ReactOS `FileDispositionInformationEx` map to `set_disposition_information()`.
- `FileEndOfFileInformation` maps to `set_end_of_file_information()` with the IRP's `AdvanceOnly` flag.
- `FileLinkInformation` and non-ReactOS `FileLinkInformationEx` map to `set_link_information()`.
- `FileRenameInformation` and non-ReactOS `FileRenameInformationEx` map to `set_rename_information()`.
- `FilePositionInformation` updates only `FileObject->CurrentByteOffset`.
- `FileValidDataLengthInformation` maps to `set_valid_data_length_information()`.
- Non-ReactOS `FileCaseSensitiveInformation` toggles the per-directory case-sensitive flag.

Readonly handling is nuanced: most set operations fail on readonly volumes or readonly subvolumes, but position changes are allowed, and the subvolume root has narrow allowances for basic/rename changes needed to manipulate subvolume readonly state or parentage.

## Basic Attributes And Disposition

`set_basic_information()` updates file times and Windows attributes. It normalizes undocumented `-2` timestamp values to "do not set", treats `-1` timestamps as "user explicitly controls this time", and updates Btrfs `INODE_ITEM` fields only for nonzero values. Attribute changes clear `FILE_ATTRIBUTE_NORMAL`, preserve directory/reparse semantics, compare against default derived attributes to decide whether DOS attributes should be deleted, and toggle `BTRFS_SUBVOL_READONLY` for subvolume roots. Successful changes bump inode transaction/sequence, mark the FCB dirty, update subvolume root ctime/ctransid for attribute changes, and queue change notifications.

`set_disposition_information()` implements delete-on-close and POSIX delete setup. It rejects deletion of readonly files, the top filesystem root, non-empty directories, and mapped image sections unless extended disposition flags allow bypassing the image-section check. It sets `fileref->delete_on_close`, `FileObject->DeletePending`, and optionally `fileref->posix_delete`; for directories it also wakes directory change notification waiters.

## Rename And Move Logic

`set_rename_information()` is the central rename path. It normalizes the target component from either the supplied target file object or a path string, validates the name, converts it to UTF-8, resolves the destination parent, enforces destination add access and replacement delete access, applies Windows/Posix replacement rules, handles readonly destination checks, and invokes `delete_fileref()` for overwritten targets with rollback support.

Same-directory renames update the existing `dir_child` name/UTF-8/upcase buffers, remove and reinsert hash-list entries, update parent directory size by the UTF-8 byte delta, bump inode and parent sequence/timestamps, mark dirty state, and emit old/new rename notifications.

Moves across directories create a deleted dummy fileref for the old location, move the live fileref under the new parent, update the directory child index/name as needed, maintain hardlink side records, update old and new parent directory sizes/timestamps, and emit removal/addition/parent modification notifications.

`move_across_subvols()` handles the harder case where the parent subvolume changes. Since Btrfs hardlinks cannot cross subvolume boundaries, this routine recursively walks child filerefs, duplicates existing FCB state into dummy FCBs, assigns new inode numbers in the destination subvolume, updates extent references for copied regular/preallocated extents, recreates directory FCBs for dummy directory placeholders, retargets subvolume parents, rewires file-reference parent/child lists, updates directory child indexes and hashes, deletes dummy records through normal delete logic, and adjusts hardlink lists. It marks both source and destination subvolume FCB versions changed.

Important rename restrictions include: the filesystem root cannot be renamed; open children block renames; non-POSIX replacement rejects open destination files or destinations with open descendants; directories cannot be overwritten as targets; readonly targets require `FILE_RENAME_IGNORE_READONLY_ATTRIBUTE`; and stream/file conversions require cache flushes first when a data section exists.

## Alternate Data Streams

WinBtrfs represents alternate data streams as xattrs with a `user.` prefix and directory-child entries with index `0`. `rename_stream()` renames an existing ADS to another ADS name. It strips an optional `:$DATA` suffix, rejects reserved internal xattr names, enforces xattr payload size limits based on Btrfs node size, updates the stream FCB's xattr name/hash/max data length, and creates a dummy deleted ADS FCB for the old xattr name so flush can remove the old on-disk item.

`rename_stream_to_file()` converts a named stream into the main unnamed file data. It requires replace semantics, refuses open or non-empty existing parent file data, transfers the parent file FCB's identity/security/metadata/children/hardlinks/xattrs into the stream FCB, marks the old parent FCB/fileref deleted, writes the ADS data as inline or regular file extents, and creates a dummy deleted ADS xattr for the former stream name.

`rename_file_to_stream()` converts a normal file into an ADS under itself. It reads the existing file data into memory, validates the new stream xattr size budget, duplicates the original FCB into a dummy deleted file, excises extents from the dummy, moves children and directory lists to the dummy, turns the live FCB into `ads=true`, creates a synthetic `dir_child` for the stream, and stores the file data in `adsdata`.

`stream_set_end_of_file_information()` resizes ADS data in memory, enforcing the stream's computed maximum xattr length. It updates the stream header sizes, parent inode ctime/sequence, parent dirty state, and subvolume root ctime/ctransid.

## Size And Cache Manager Updates

`set_end_of_file_information()` handles both allocation/preallocation and EOF changes. For ADS, it delegates to `stream_set_end_of_file_information()` and sends stream-size notifications. For normal files, it rejects deleted filerefs, clamps lazy-writer advance-only requests that try to page-align file size, uses `MmCanFileBeTruncated()` before truncation, calls `truncate_file()` or `extend_file()`, updates write time unless the user set it, marks dirty state, queues size notifications, applies rollback on failure, and calls `CcSetFileSizes()` inside SEH after releasing the FCB resource.

`set_valid_data_length_information()` validates the input size, rejects sparse files, enforces monotonic VDL within file size, then updates cache-manager file sizes and inode write time/dirty state. The file notes this is mostly a semantic stub because the filesystem already treats VDL as effectively maximal.

## Hardlink Support

`set_link_information()` creates NT hardlinks for regular non-ADS files. It validates name and destination, rejects directory or stream hardlinks, enforces a 65535 link count limit, prevents hardlinks across subvolume boundaries, handles replacement via `delete_fileref()`, creates a new file reference and directory child in the destination, builds or extends the FCB hardlink side list, increments `st_nlink`, updates inode and parent metadata, and sends an added-name notification.

`fill_in_hard_link_information()` and `fill_in_hard_link_full_id_information()` enumerate hardlinks. They special-case subvolume roots, otherwise use the FCB hardlink list when present and fall back to the current fileref for single-link files. Enumeration resolves parent filerefs by inode, skips deleted visible entries, reports required byte counts, handles aligned variable-length entries, and supports both 64-bit parent inode IDs and 128-bit parent file IDs containing inode plus subvolume ID.

## Query Information

`query_info()` serves `IRP_MJ_QUERY_INFORMATION`. It rejects volume FCBs and missing CCBs, performs per-class access checks for attribute-bearing queries, fills requested structures, computes `IoStatus.Information` from remaining buffer length, and maps negative remaining length to `STATUS_BUFFER_OVERFLOW`.

The fill helpers translate Btrfs metadata into Windows views:
- `fill_in_file_basic_information()` returns creation/access/write/change times and file attributes, using parent attributes for ADS.
- `fill_in_file_standard_information()` returns allocation size, EOF, link count, delete-pending flag, and directory flag.
- `fill_in_file_network_open_information()` provides the compact network-open view with directory EOF set to zero.
- `fill_in_file_internal_information()` uses `make_file_id(subvol, inode)`.
- `fill_in_file_name_information()` builds a full path from the fileref chain and appends `:$DATA` for ADS.
- `fill_in_file_stream_information()` reports the unnamed data stream plus ADS entries from index-0 directory children.
- `fill_in_file_attribute_information()` returns attributes and reparse tags.
- `fill_in_file_compression_information()` reports compressed size as logical ADS or file size.
- Non-ReactOS helpers fill hardlink, file ID, stat, LX stat, standard link, and case-sensitive directory information.

`fileref_get_filename()` walks from a file reference to the root, prepending `\` for normal path components and `:` for ADS components. It supports truncation reporting via `STATUS_BUFFER_OVERFLOW`, returns `\` for the root fileref, and reports a name offset used by rename notifications.

`fill_in_file_stat_information()` and `fill_in_file_stat_lx_information()` expose Windows 10 stat views. They map Btrfs socket/FIFO/char/block device types to LX/AF_UNIX reparse tags, force `FILE_ATTRIBUTE_REPARSE_POINT` for those special types, report effective access from the CCB, and include UID/GID/mode/device IDs in the LX variant.

## Extended Attributes And LX Metadata

`drv_query_ea()` maps the user output buffer, validates object/access state, redirects ADS queries to the parent file FCB, and returns EAs from `fcb->ea_xattr`. It supports explicit EA-name lists, restart scans, index-specified scans, single-entry returns, 4-byte entry padding, `ccb->ea_index` continuation state, `STATUS_NO_EAS_ON_FILE`, `STATUS_NO_MORE_EAS`, `STATUS_BUFFER_TOO_SMALL`, and `STATUS_BUFFER_OVERFLOW`.

`drv_set_ea()` validates the input EA buffer with `IoCheckEaBufferValidity()`, redirects ADS writes to the parent file, converts existing EA records into a temporary `ea_item` list, merges incoming records case-insensitively after uppercasing names, removes zero-length values, and repacks the remaining EAs into a contiguous `FILE_FULL_EA_INFORMATION` buffer.

The setter consumes special LXSS EAs for UID, GID, and mode rather than storing them as ordinary EAs. UID and mode updates require kernel mode or `FILE_WRITE_ATTRIBUTES`; UID changes also mark the security descriptor dirty. Mode updates preserve only permission and special mode bits. After repacking, the routine marks EA state changed, bumps inode transaction/sequence/ctime, marks the FCB dirty, and sends an EA change notification.

## Locking, Rollback, And Dirty State

This file uses `Vcb->tree_lock`, `Vcb->fileref_lock`, per-FCB `Header.Resource`, and per-directory `dir_children_lock` extensively. Rename and link paths generally acquire tree lock shared, fileref lock exclusive, and the target FCB resource exclusive before mutating fileref and directory state. Cross-subvolume moves additionally hold the global FCB lock while moving FCBs between subvolume lists.

Operations that mutate on-disk metadata often initialize a rollback list and call `clear_rollback()` on success or `do_rollback()` on failure. Dirty FCBs and filerefs are marked through helpers from other modules, ensuring the flush path later writes INODE_ITEMs, xattrs, directory items, extents, and deleted dummy records.

Directory child hash maintenance uses two sorted hash lists per directory, one case-sensitive and one upcased, with 256 bucket shortcut arrays. `insert_dir_child_into_hash_lists()` inserts by CRC32C hash order and updates bucket heads; `remove_dir_child_from_hash_lists()` removes entries and repairs affected bucket pointers.

## Dependencies

This file depends on Windows kernel/IFS APIs for IRP dispatch, file information structures, resources, cache-manager size updates and flushes, section-object deletion checks, security subject capture and access checks, EA validation, oplock checks, directory notifications, user-buffer mapping, and top-level filesystem IRP tracking.

It depends on the wider Btrfs driver for FCB/file-reference allocation and lifetime, dirty marking, rollback, directory opening and child creation, name validation/conversion, extent truncation/extension/excision/reference updates, xattr constants, file attribute derivation, reparse tag lookup, inode ID construction, cache-size helpers, subvolume readonly checks, tree flushing, and notification queuing.

## Important Invariants And Risks

- ADS handling assumes stream data fits into a single xattr-sized buffer; `adsmaxlen` derived from node size is the hard capacity limit for stream resize and file-to-stream conversion.
- Rename/file-to-stream/stream-to-file conversions transfer ownership of many pointers between FCBs and filerefs. These paths rely on careful nulling of moved fields to avoid double frees and on dummy deleted objects so flush removes old metadata.
- Cross-subvolume moves are not simple renames: they create new inodes and update extent references. Any missed extent, xattr, hardlink, or child reference update could leak references or leave inconsistent metadata.
- Parent directory `st_size` is maintained as twice UTF-8 name length in several paths. Bugs in old/new length accounting would affect directory metadata consistency.
- Hardlink side lists are used as persistent enumeration aids and must stay synchronized with directory child moves, replacements, and link creation.
- Many paths allocate memory after partially mutating in-memory structures. Rollback covers on-disk metadata operations, but pointer ownership and list integrity still depend on each error branch leaving structures coherent.
- Query helpers often subtract from a signed `LONG length`; callers convert negative remaining length to `STATUS_BUFFER_OVERFLOW`. Individual helpers must still avoid writing past the caller's actual buffer.
- `fileref_get_filename()` has an explicit FIXME about needing a fileref filepart lock, so concurrent rename/name query interactions are a known synchronization concern.
- ReactOS builds exclude several Windows 10 information classes and case-sensitive set/query paths guarded by `#ifndef __REACTOS__`; behavior differs from non-ReactOS WinBtrfs builds.
- Delete, rename, and hardlink replacement semantics combine Windows readonly rules, POSIX flags, image-section checks, open-count checks, and subvolume restrictions; these are high-risk compatibility surfaces.
