# File Research: sources/os/linux/linux-stable/fs/ntfs/inode.c

## Scope

This file is the central NTFS inode and attribute-inode implementation. It covers VFS inode lookup/initialization, fake inodes for attributes and indexes, mount-time `$MFT` bootstrap, MFT/attribute parsing, extent inode attachment, inode writeback, eviction/deletion, mount option reporting, initialized-size extension, MFT record free-space management, and raw pread/pwrite for attribute inodes.

## APIs And Control Flow

- `ntfs_test_inode()` and `ntfs_init_locked_inode()` implement `iget5_locked()` matching/initialization for normal inodes and fake attribute/index inodes.
- `ntfs_iget()`, `ntfs_attr_iget()`, and `ntfs_index_iget()` obtain normal, attribute, and index inodes respectively, invoking specialized locked-read routines for new inodes.
- `ntfs_alloc_big_inode()` / `ntfs_free_big_inode()` allocate the VFS-embedded `struct ntfs_inode`.
- `__ntfs_init_inode()` initializes NTFS inode fields, locks, runlists, extent state, index/compression union fields, and lockdep classes.
- `ntfs_read_locked_inode()` loads normal MFT records, validates base records/link counts, reads `$STANDARD_INFORMATION`, loads `$ATTRIBUTE_LIST`, detects WSL EAs, applies mode masks, handles directories and regular files, detects reparse symlinks, recognizes extended system files such as `$Reparse` and `$ObjId`, and configures VFS operations.
- `ntfs_read_locked_attr_inode()` mirrors base inode metadata onto fake attribute inodes and loads resident/non-resident attribute sizes, compression/sparse/encryption state, and block accounting.
- `ntfs_read_locked_index_inode()` loads named index metadata from `$INDEX_ROOT`, validates index sizing/collation, loads `$INDEX_ALLOCATION` and `$BITMAP` for large indexes, checks bitmap coverage, and attaches the base inode.
- `ntfs_read_inode_mount()` bootstraps `$MFT` during mount before normal page-cache MFT mapping is available. It reads record 0 directly from the block device, applies MST fixups, optionally loads `$ATTRIBUTE_LIST`, decompresses `$MFT/$DATA` mapping pairs extent by extent, then re-enters normal inode loading once the first `$MFT` run is known.
- `ntfs_evict_big_inode()` truncates page cache, deletes unlinked base inodes and their clusters/MFT records, commits dirty linked inodes, releases extents, frees attribute lists/runlists/names/reparse targets, and drops base references for fake inodes.
- `ntfs_show_options()` prints NTFS mount options: uid/gid, masks, charset, case mode, system/hidden behavior, error policy, MFT zone multiplier, immutable system files, Windows-name checks, discard, sparse disabling, and ACL mode.
- `ntfs_extend_initialized_size()` maps runlists, zeroes gaps for uncompressed non-resident attributes, optionally synchronizes zeroed pages, and updates initialized size in metadata.
- `ntfs_truncate_vfs()` wraps NTFS attribute truncation under `mrec_lock` and updates mtime/ctime.
- `ntfs_inode_sync_standard_information()` synchronizes NTFS standard information timestamps and file attributes without causing infinite dirty-write loops.
- `ntfs_inode_sync_filename()` updates all parent directory filename index entries with current file attributes, sizes, reparse tags, and timestamps.
- `__ntfs_write_inode()` writes dirty base inodes and attached extent MFT records, updates mapping pairs for dirty runlists, syncs standard info and filename entries, resolves MFT record LCNs, and reports volume errors on non-memory failures.
- `ntfs_inode_attach_all_extents()` and `ntfs_extent_inode_open()` load and attach all extent MFT records referenced by an attribute list.
- `ntfs_inode_add_attrlist()` builds an in-memory attribute list from existing attributes, frees MFT record space if needed by moving attributes away, adds `$ATTRIBUTE_LIST`, updates it, and rolls back on failure.
- `ntfs_inode_free_space()` tries to free space in a base MFT record by moving movable attributes to extent records, preserving `$STANDARD_INFORMATION`, `$ATTRIBUTE_LIST`, `$MFT/$DATA`, and `$INDEX_ROOT`.
- `ntfs_inode_attr_pread()` reads fake attribute inode data from resident attribute memory or non-resident page-cache folios.
- `ntfs_inode_attr_pwrite()` enlarges attributes as needed, then writes resident data into the MFT record and page cache or writes non-resident folios, optionally issuing synchronous bio writes to mapped clusters.
- `ntfs_get_locked_folio()` is a helper that first tries to lock an existing folio and otherwise submits readahead and reads it.

## State And Dependencies

Important state includes inode NTFS flags, VFS mode/timestamps/link count, MFT sequence numbers, runlists, attribute lists, extent inode arrays, base/fake inode relationships, `mrec_lock`, `runlist.lock`, `extent_lock`, initialized/data/allocated/compressed sizes, MFT record LCN cache, and volume mount options.

This file depends on nearly every NTFS subsystem: MFT mapping and writeback, attribute search/update/truncate, mapping-pair decompression, runlist merge/free, cluster allocation/free, index mutation, EA/WSL metadata, reparse and object-id indexes, iomap zeroing, bitmap files, and block-device reads/writes.

## Risks And Invariants

- Normal inodes, fake attribute inodes, index inodes, and extent inodes have different lifetime and locking rules. `nr_extents == -1` marks fake/extent-attached behavior and must be interpreted carefully.
- `$MFT` mount bootstrap is circular by nature; it relies on discovering enough `$MFT/$DATA` mapping information to safely enable normal MFT page-cache access.
- Attribute-list handling is delicate: entries may refer to extent records, rollback must move attributes back, and `$ATTRIBUTE_LIST` itself cannot be casually moved out of the base record.
- Inode writeback deliberately ignores dirty fake attribute inodes because their real storage is written through the base inode.
- Filename sync touches parent directory indexes and can deadlock during unmount if run while the superblock is inactive; the code skips that path when `SB_ACTIVE` is absent.
- Deleting unlinked base inodes frees non-resident clusters, extent MFT records, and the base MFT record; failures leave inconsistent metadata and are logged.
- Raw attribute pwrite with `sync=true` bypasses buffered dirty writeback by constructing bios from runlist mappings; correctness depends on valid runlists and cluster/page offset calculations.
- Many corruption checks mark volume errors and ask for `chkdsk`; `-ENOMEM` is treated as retryable and does not poison the volume.
