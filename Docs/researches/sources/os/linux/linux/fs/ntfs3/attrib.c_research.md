# File Research: sources/os/linux/linux/fs/ntfs3/attrib.c

Read coverage: complete file, 2776 lines.

This is the ntfs3 attribute allocation and mutation engine. It manipulates resident/nonresident attributes, runlists, delayed allocation, sparse/compressed data, WOF compression metadata, file size changes, and fallocate-style range operations.

Key functions:
- `attr_load_runs()` and `attr_load_runs_vcn()` unpack nonresident mapping pairs into run trees.
- `run_deallocate_ex()` frees physical clusters from run ranges, optionally trims and reconciles delayed-allocation runs.
- `attr_allocate_clusters()` finds free clusters, inserts runlist entries, handles preallocation, MFT-zone allocation, zeroout requests, delayed-allocation removal, and rollback on failure.
- `attr_make_nonresident()` converts a resident attribute into a nonresident one, copying existing data into allocated clusters or page cache and restoring metadata on failure.
- `attr_set_size_ex()` is the central resize path for resident/nonresident attributes. It handles growth, shrink, preallocation, delayed allocation, sparse/compressed attributes, multi-segment attributes, attribute-list creation/expansion, MFT special cases, size/valid-size/alloc-size updates, and rollback paths.
- `attr_data_get_block()` / `_locked()` map VCN to LCN, allocate sparse holes on demand, return special LCN values for resident, EOF, delayed, sparse, and compressed cases, and manage compressed-frame-aligned allocation.
- `attr_data_write_resident()` writes a dirty folio back into a resident `$DATA` attribute.
- `attr_load_runs_range()` ensures runlist coverage for byte ranges.
- `attr_wof_frame_info()` under `CONFIG_NTFS3_LZX_XPRESS` reads WOF compressed frame offset tables from resident or nonresident WOF data.
- `attr_is_frame_compressed()` detects whether an NTFS compression frame has sparse tail clusters.
- `attr_allocate_frame()` adjusts physical clusters for an LZNT compressed frame and updates total allocated size.
- `attr_collapse_range()`, `attr_punch_hole()`, and `attr_insert_range()` implement aligned range removal, sparse hole punching, and hole insertion for extended attributes.
- `attr_force_nonresident()` forces the default data attribute out of resident form.

Integration:
- Heavily depends on ntfs3 runlist, bitmap, MFT-record, attribute-list, inode, delayed-allocation, and compression helpers.
- Called from file I/O, fallocate, compression, inode growth/truncation, and metadata maintenance paths.
- Coordinates VFS inode size/bytes, `ni->i_valid`, parent duplicate-info update flags, and dirty inode/MFT state.

Risks and invariants:
- Most operations mutate both runlists and packed on-disk mapping pairs; rollback paths are critical.
- Attribute-list layout can change mid-operation, so many paths re-find base attributes after insertion or expansion.
- Delayed allocation and real allocation coexist; callers must hold `ni->file.run_lock` and `ni_lock()` as documented by each path.
- Sparse/compressed files require frame alignment and special total-size accounting.
- Several unrecoverable deep failures mark the inode bad because reconstructing prior multi-segment state is too complex.
