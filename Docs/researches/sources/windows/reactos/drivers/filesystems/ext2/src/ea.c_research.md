# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ea.c

This file implements Windows extended-attribute query and set operations over ext4 xattr storage. It translates between Windows `FILE_FULL_EA_INFORMATION` buffers and libext-style `ext4_xattr_ref` items in the `EXT4_XATTR_INDEX_USER` namespace.

Key responsibilities:
- Enumerate all user xattrs, a single indexed xattr, or a caller-specified EA list.
- Format EA query results as linked Windows full-EA records.
- Validate EA names using Windows/FAT-compatible ANSI-name rules.
- Replace a file's user EA set from a caller-provided full-EA buffer.
- Serialize EA access with FCB resources and xattr reference lifetime management.

Important functions:
- `Ext2IterateAllEa`: Iterator callback that copies one xattr item into a `FILE_FULL_EA_INFORMATION` record, links it from the previous record, tracks remaining output space, and stops on overflow or single-entry mode.
- `Ext2QueryEa`: Parses query flags and buffers, acquires `Fcb->MainResource`, obtains an xattr reference, handles named EA-list queries, index-based single queries, or normal scans, updates `Ccb->EaIndex`, and reports output byte count.
- `Ext2IsEaNameValid`: Rejects empty or over-255-byte names and checks each non-DBCS byte with `FsRtlIsAnsiCharacterLegalFat`.
- `Ext2SetEa`: Validates the caller EA buffer with `IoCheckEaBufferValidity`, acquires `Vcb->FcbLock` and `Fcb->MainResource`, purges existing xattr items, validates all incoming names, and adds each EA through `ext4_fs_set_xattr_ordered`.

Important interactions:
- Uses `ext4_fs_get_xattr_ref`, `ext4_fs_get_xattr`, `ext4_fs_xattr_iterate`, `ext4_xattr_purge_items`, `ext4_fs_set_xattr_ordered`, and `ext4_fs_put_xattr_ref`.
- Reports EA changes through `Ext2NotifyReportChange` with `FILE_NOTIFY_CHANGE_EA`.
- Defers non-waitable work through `Ext2QueueRequest` in the same style as other IRP handlers.

Notable behavior and risks:
- `Ext2SetEa` purges existing EA items before validating and adding the new set; failure later clears `xattr_ref.dirty` before putting the reference, relying on the xattr layer to discard uncommitted changes.
- `Ext2QueryEa` emits a change notification on successful query, which is unusual because queries do not modify EA state.
- EA values are copied after a null byte following the EA name, matching Windows full-EA layout.
- Index scans use one-based `EaIndex`/`EaIndexCounter` semantics.
