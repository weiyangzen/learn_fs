# File Research: sources/os/linux/linux-stable/fs/ntfs3/frecord.c

## Summary
Implements NTFS3 MFT-record and file-record management for `struct ntfs_inode`. It owns MFT subrecord loading/caching, attribute discovery and insertion/removal, attribute-list creation/expansion/compaction, whole-inode deletion, filename attribute maintenance, sparse/compressed flag transitions, reparse interpretation, compressed frame I/O, directory name updates, inode dirtiness/writeback, parent duplicate-info propagation, and delayed-allocation materialization.

## Main Responsibilities
- Maintain the per-inode red-black tree of loaded extension MFT records.
- Locate, enumerate, insert, remove, and move attributes across primary and extension records.
- Create, update, expand, shrink, and remove NTFS `$ATTRIBUTE_LIST` data.
- Allocate and free child MFT records for attributes that do not fit in the base record.
- Delete all attributes and deallocate all nonresident runs when an unlinked inode is cleared.
- Implement native LZNT compressed frame reads/writes and optional WOF LZX/XPRESS external decompression.
- Maintain `$FILE_NAME` attributes and parent directory indexes during link removal, add, undo, and rename.
- Write dirty base and extension MFT records, update standard information, update parent duplicate records, and free empty extension records.
- Allocate delayed-allocation clusters before direct I/O, close, or other paths that require real mappings.

## Key Interfaces
- MFT subrecord helpers: `ni_load_mi_ex()`, `ni_load_mi()`, `ni_load_all_mi()`, `ni_add_subrecord()`, `ni_remove_mi()`.
- Attribute lookup/enumeration: `ni_find_attr()`, `ni_enum_attr_ex()`, `ni_std()`, `ni_std5()`.
- Attribute mutation: `ni_insert_resident()`, `ni_insert_nonresident()`, `ni_remove_attr()`, `ni_remove_attr_le()`, `ni_create_attr_list()`, `ni_expand_list()`.
- Cleanup and deletion: `ni_clear()`, `ni_delete_all()`.
- Compression/reparse: `ni_parse_reparse()`, `ni_read_folio_cmpr()`, `ni_read_frame()`, `ni_write_frame()`, and `ni_decompress_file()` when LZX/XPRESS support is compiled in.
- Name operations: `ni_fname_name()`, `ni_fname_type()`, `ni_remove_name()`, `ni_remove_name_undo()`, `ni_add_name()`, `ni_rename()`.
- Writeback and allocation: `ni_is_dirty()`, `ni_write_parents()`, `ni_write_inode()`, `ni_allocate_da_blocks()`, `ni_allocate_da_blocks_locked()`.

## Important Behavior
`ni_find_attr()` switches between simple base-record lookup and attribute-list lookup. When an attribute list is present, it finds the list entry, loads the referenced MFT record, finds the concrete attribute by id, and validates VCN coverage. Inconsistency marks the VFS inode bad.

Attribute insertion first tries the primary MFT record, then extension records, then allocates a new child record. `$STANDARD_INFORMATION`, `$ATTRIBUTE_LIST`, and `$LogFile` attributes cannot be externalized. `$MFT::$DATA` is special: its first segment must remain in the base MFT record, so insertion can evict other attributes or split the MFT data attribute through `ni_expand_mft_list()`.

`ni_create_attr_list()` builds an attribute list from base-record attributes and moves enough movable attributes to a child record to fit the resident list. `ni_try_remove_attr_list()` performs the reverse optimization when all attributes can fit back into the primary record, copying a backup of the MFT record so it can restore the primary record on failure.

`ni_delete_all()` enumerates all attributes, removes NTFS3 reparse/object-id side records when relevant, deallocates every nonresident run by unpacking mapping pairs with `RUN_DEALLOCATE`, deallocates the attribute-list run, frees child MFT records, marks the base record free, and updates the MFT bitmap.

`ni_new_attr_flags()` handles sparse/compressed flag changes only for empty data attributes. It prevents simultaneous sparse and compressed flags, resizes the nonresident attribute header between normal and extended forms, updates compression unit state, and switches the inode mapping aops between normal and compressed address-space operations.

`ni_parse_reparse()` recognizes symlink/mount-point style name-surrogate reparses, WOF external compression reparses, and dedup reparses. WOF parsing records the external compression frame size in inode flags; dedup marks the inode as deduplicated so higher-level I/O paths reject unsupported access.

Compressed-frame I/O maps a whole compression frame with `vmap()`. Native LZNT reads detect resident data, sparse frames, uncompressed frames, and compressed frames; writes compress the page array, choose sparse/compressed/uncompressed frame layout, update allocation through `attr_allocate_frame()`, and write packed data to the runlist. Optional WOF decompression reads `WofCompressedData`, uses shared LZX/XPRESS decompressor contexts, writes decompressed data to normal data runs, removes WOF/reparse attributes, and clears cached compression state.

Name operations deliberately add the new name before removing the old name during rename. This avoids the harder failure mode where the old name is removed but the new one cannot be allocated and restoration fails. Removal tracks undo state for paired DOS/Win32 names.

`ni_write_inode()` updates timestamps and file attributes in `$STANDARD_INFORMATION`, updates parent directory duplicate information unless the inode is metadata or inactive, writes dirty attribute lists, writes dirty child records, frees empty child records, and finally writes the base record. If parent indexes cannot be locked, it leaves `NI_FLAG_UPDATE_PARENT` set and redirties the inode for a later pass.

## State and Synchronization
The file uses `ni_lock()` around inode metadata mutation, `ni->file.run_lock` around runlist and data-size mutations, page and folio locks for compressed I/O, and the inode dirty flag protocol for MFT writeback. Child MFT records live in `ni->mi_tree`; attribute-list state is in `ni->attr_list`; file data run state is in `ni->file.run` and delayed allocation in `ni->file.run_da`.

## Cross-File Interactions
This file is the metadata backend used by `file.c`, `inode.c`, `namei.c`, `index.c`, `attrib.c`, and mount/writeback code. It depends on `mi_*` record primitives, `al_*` attribute-list helpers, `run_*` mapping-pair helpers, `attr_*` allocation/size/frame helpers, `indx_*` directory index helpers, object-id and reparse indexes, LZNT/LZX/XPRESS library code, and VFS inode lookup/writeback.

## Risks
Attribute-list and extension-record code is pointer-sensitive: adding a list entry can resize/move list storage, and moving attributes invalidates pointers into MFT records. The `$MFT::$DATA` bootstrap rules are fragile because extension record placement must not conflict with MFT data coverage. Compression paths must keep frame size, page count, runlist locking, and valid-size zeroing consistent. Parent duplicate-info updates are best-effort and can defer through dirty flags, so writeback ordering matters. `ni_clear()` can delete all metadata for an unlinked inode unless log replay is active, making link count and replay flags critical.
