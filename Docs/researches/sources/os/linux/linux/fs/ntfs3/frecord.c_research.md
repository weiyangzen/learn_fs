# File Research: sources/os/linux/linux/fs/ntfs3/frecord.c

## Purpose

Implements NTFS file-record (`MFT_REC`) management for `ntfs3`. It presents a coherent `ntfs_inode` view across the base MFT record, external subrecords, attribute-list entries, resident/nonresident attributes, names, compression frames, parent-directory duplicate metadata, dirty writes, and delayed allocation.

## Main Interfaces

- MFT/subrecord lifecycle: `ni_load_mi_ex()`, `ni_load_mi()`, `ni_load_all_mi()`, `ni_add_subrecord()`, `ni_remove_mi()`, `ni_clear()`.
- Attribute discovery/enumeration: `ni_find_attr()`, `ni_enum_attr_ex()`, `ni_std()`, `ni_std5()`.
- Attribute mutation: `ni_insert_resident()`, `ni_insert_nonresident()`, `ni_remove_attr()`, `ni_remove_attr_le()`, `ni_new_attr_flags()`.
- Attribute-list management: `ni_create_attr_list()`, `ni_expand_list()`, internal `ni_try_remove_attr_list()`, `ni_ins_attr_ext()`.
- File deletion: `ni_delete_all()`.
- Names and rename: `ni_fname_name()`, `ni_fname_type()`, `ni_add_name()`, `ni_remove_name()`, `ni_remove_name_undo()`, `ni_rename()`.
- Compression: `ni_parse_reparse()`, `ni_read_folio_cmpr()`, `ni_read_frame()`, `ni_write_frame()`, and, with `CONFIG_NTFS3_LZX_XPRESS`, `ni_decompress_file()`.
- Writeback: `ni_is_dirty()`, `ni_write_inode()`, `ni_write_parents()`.
- Delayed allocation: `ni_allocate_da_blocks()`, `ni_allocate_da_blocks_locked()`.
- Seeking: `ni_seek_data_or_hole()`.

## Key Behavior

- Subrecords are cached in `ni->mi_tree`, keyed by record number, and loaded lazily through attribute-list entries.
- `ni_find_attr()` chooses the base record fast path when there is no attribute list, otherwise resolves the list entry, loads the containing subrecord, validates VCN coverage, and marks the inode bad on inconsistencies.
- Attribute insertion prefers the base record, creates an attribute list when required, and spills eligible attributes into external records when the base record lacks space.
- `$MFT::$DATA` has special handling: its first data segment must remain in the base record, so other attributes may be moved out to make room.
- Attribute-list shrink/removal is attempted during writeback when all attributes can fit back into the base record.
- `ni_delete_all()` deallocates nonresident runs, removes NTFS3 object IDs/reparse records, frees attribute-list runs, frees subrecords, clears the base record in-use bit, writes records, and returns MFT records to the free set.
- `ni_new_attr_flags()` only allows sparse/compressed flag changes for empty nonresident files and ensures a file cannot be both sparse and compressed.
- `ni_parse_reparse()` recognizes symlink/mount-point style reparse points, WOF compressed files, and deduplicated files; WOF compression sets external compression bits for later frame reads.
- Native compressed reads/writes operate on compression frames. `ni_read_frame()` handles resident data, valid-size zeroing, native LZNT, and optional external LZX/XPRESS WOF data. `ni_write_frame()` compresses LZNT frames and updates allocated/sparse frame state.
- `ni_decompress_file()` converts WOF compressed files back to normal data by allocating clusters, reading/decompressing frames into the normal data stream, removing `WofCompressedData` and reparse attributes, and clearing sparse/reparse/compression cached state.
- Rename prefers add-new-name then remove-old-name to reduce failure risk, with undo support for the alternate strategy kept in code.
- `ni_write_inode()` updates standard info timestamps/flags, parent directory duplicate info, attribute lists, dirty subrecords, and the base MFT record. Empty dirty subrecords are freed.

## Dependencies

- MFT record helpers: `mi_get`, `mi_put`, `mi_write`, `mi_find_attr`, `mi_insert_attr`, `mi_remove_attr`, `mi_resize_attr`, `mi_pack_runs`.
- Attribute-list helpers: `al_find_ex`, `al_enumerate`, `al_add_le`, `al_remove_le`, `al_update`, `al_destroy`.
- Run/cluster helpers: `run_pack`, `run_unpack`, `run_deallocate`, `run_add_entry`, `ntfs_read_run`, `ntfs_write_run`.
- Directory index helpers: `indx_insert_entry`, `indx_delete_entry`, `indx_update_dup`.
- Compression helpers: LZNT always; LZX/XPRESS under `CONFIG_NTFS3_LZX_XPRESS`.
- VFS integration: page cache folios, inode timestamps, `ntfs_iget5()`, `mark_inode_dirty()`.

## Error and Safety Notes

- Attribute-list and subrecord operations are tightly coupled; many failures mark the inode bad or return `-EINVAL`.
- Several paths are intentionally best-effort, especially attribute-list repacking/removal and parent duplicate updates.
- Compression paths rely on full-frame locking and must carefully unlock/put every folio on failures.
- `ni_write_inode()` avoids blocking on busy inodes by re-dirtying and returning when `ni_trylock()` fails.
- Delayed allocation is resolved differently for sparse and normal files: sparse files allocate through `attr_data_get_block_locked()`, normal files through `attr_set_size_ex()`.
