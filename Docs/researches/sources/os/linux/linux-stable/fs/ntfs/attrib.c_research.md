# File Research: sources/os/linux/linux-stable/fs/ntfs/attrib.c

Purpose: Core NTFS attribute implementation. This file owns attribute lookup, runlist mapping, resident/non-resident conversion, attribute creation/removal, mapping-pair persistence, truncate/expand/fallocate behavior, range insert/collapse/punch operations, and whole-attribute reads.

Key responsibilities:
- Maps virtual cluster numbers to runlist/LCN state through `ntfs_map_runlist_nolock()`, `ntfs_map_runlist()`, `ntfs_attr_vcn_to_lcn_nolock()`, `ntfs_attr_find_vcn_nolock()`, and `ntfs_attr_map_whole_runlist()`.
- Searches MFT attributes with `ntfs_attr_find()`, `ntfs_external_attr_find()`, and `ntfs_attr_lookup()`, including attribute-list-backed extents and continuation semantics through `struct ntfs_attr_search_ctx`.
- Validates attribute record bounds aggressively: record length, name offset, resident value offset/length, nonresident mapping-pair offset, minimum value sizes for known resident attributes, and attribute-list ordering.
- Converts attributes between resident and non-resident forms via `ntfs_attr_make_non_resident()` and `ntfs_attr_make_resident()`.
- Adds, removes, resizes, and moves attribute records with `ntfs_attr_record_resize()`, `ntfs_resident_attr_record_add()`, `ntfs_non_resident_attr_record_add()`, `ntfs_attr_record_rm()`, `ntfs_attr_add()`, `ntfs_attr_record_move_to()`, and `ntfs_attr_record_move_away()`.
- Rebuilds mapping pairs and attribute extents with `ntfs_attr_update_mapping_pairs()`, including sparse/compressed metadata updates and allocation of new extent MFT records when mapping pairs no longer fit.
- Handles size changes through `ntfs_attr_expand()`, `ntfs_attr_truncate_i()`, `ntfs_attr_truncate()`, `__ntfs_attr_truncate_vfs()`, `ntfs_non_resident_attr_expand()`, `ntfs_non_resident_attr_shrink()`, and `ntfs_resident_attr_resize()`.
- Implements cluster materialization for holes/delalloc via `ntfs_attr_map_cluster()` and higher-level allocation through `ntfs_attr_fallocate()`.
- Supports range operations for nonresident unnamed `$DATA`: `ntfs_non_resident_attr_insert_range()`, `ntfs_non_resident_attr_collapse_range()`, and `ntfs_non_resident_attr_punch_hole()`.
- Provides convenience helpers for attribute existence/removal/read-all/name conversion.

Important data and invariants:
- `AT_UNNAMED` is the canonical unnamed attribute marker.
- Runlist updates require correct locking: most mapping paths require `ni->runlist.lock`; conversion/truncate/fallocate also interact with `mrec_lock`.
- Search contexts may map base and extent MFT records and must be released with `ntfs_attr_put_search_ctx()`.
- Attribute-list presence changes lookup semantics; operations must keep `base_ni->attr_list`, on-disk `$ATTRIBUTE_LIST`, and per-record attribute entries synchronized.
- First nonresident attribute extent carries allocated/data/initialized/compressed size metadata.
- Sparse state is inferred from runlist contents and mirrored into inode flags, attribute flags, compressed-size field presence, and filename-dirty state.
- `$MFT::$DATA` is protected from truncate/expand paths.
- Encrypted attributes are largely unsupported for resize/truncate and return errors.

Key dependencies:
- `attrlist.c` for attribute-list entry add/remove/update.
- `lcnalloc` and runlist helpers for cluster allocation, freeing, merging, truncation, sparse detection, and mapping-pair build/decompress.
- `mft` and inode helpers for MFT record mapping, extent allocation, dirty marking, inode open/close, and attrlist creation.
- `iomap`/direct I/O zeroing for fallocate hole materialization.

Error handling and risk notes:
- Many corruption paths convert lookup or mapping failures to `-EIO` and set volume errors for chkdsk-style recovery.
- Rollback is best-effort in resident-to-nonresident conversion and nonresident expansion; failures can leave leaked clusters or inconsistent metadata, with explicit error logs.
- Several paths intentionally continue after cleanup failures to preserve metadata consistency as much as possible.
- `ntfs_resident_attr_record_add()` and `ntfs_non_resident_attr_record_add()` return offsets on success, but some failure paths normalize to `-EIO` or `-1`; callers must not assume all errno values are preserved.
- `ntfs_attr_update_mapping_pairs()` is central and high risk: it can resize records, move attributes, add attrlists, allocate new extents, delete obsolete extents, and update compressed/sparse accounting.
