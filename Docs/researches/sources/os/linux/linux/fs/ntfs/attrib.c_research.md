# File Research: sources/os/linux/linux/fs/ntfs/attrib.c

Implements the Linux NTFS driver's core attribute engine: attribute lookup, attribute-list traversal, resident/non-resident conversion, runlist mapping, mapping-pairs rewrite, attribute insertion/removal, truncation/expansion, cluster mapping, hole punching, range insert/collapse, and fallocate support.

Key entry points:
- `ntfs_map_runlist_nolock()` / `ntfs_map_runlist()` map compressed on-disk mapping pairs into `ni->runlist`, preserving caller search-context state when provided.
- `ntfs_attr_vcn_to_lcn_nolock()`, `ntfs_attr_find_vcn_nolock()`, and `ntfs_attr_vcn_to_rl()` translate or locate VCNs, retrying once after mapping missing runlist fragments.
- `ntfs_attr_lookup()` is the public search API; it dispatches to direct MFT-record search or attribute-list-aware external search.
- `ntfs_attr_open()` initializes an NTFS attribute inode from an attribute record, including resident/non-resident size state, compression/sparse/encryption flags, and named stream handling.
- `ntfs_attr_update_mapping_pairs()` is the central metadata commit path after runlist edits.
- `ntfs_attr_truncate()`, `ntfs_attr_expand()`, `ntfs_attr_map_cluster()`, and `ntfs_attr_fallocate()` expose size growth, allocation, and preallocation behavior.
- `ntfs_attr_rm()`, `ntfs_attr_add()`, `ntfs_attr_remove()`, `ntfs_attr_readall()`, `ntfs_non_resident_attr_insert_range()`, `ntfs_non_resident_attr_collapse_range()`, and `ntfs_non_resident_attr_punch_hole()` provide higher-level metadata operations.

Core mechanics:
- Attribute search relies on NTFS sort order by type, name, and resident value. `ntfs_attr_find()` scans one MFT record and validates record lengths, name bounds, resident value bounds, non-resident mapping-pairs offsets, and minimum resident sizes for known attribute types.
- `ntfs_external_attr_find()` walks `$ATTRIBUTE_LIST`, maps extent MFT records, validates list entries and stale MFT references, and returns both the found attribute record and its attribute-list entry.
- Search contexts carry current MFT record, current attribute, base record state, mapped extent state, and current attribute-list entry. Context reinitialization must unmap extent records and restore base-record pointers safely.
- Runlist mapping decompresses only the needed extent for a VCN unless whole-runlist mapping is requested. Whole mapping enumerates extents by increasing `lowest_vcn`/`highest_vcn` and marks `NInoFullyMapped`.
- Resident-to-non-resident conversion allocates clusters, builds mapping pairs, writes non-resident record fields, updates inode sizes and compressed metadata, then flips `NInoNonResident` only after the record is internally consistent.
- Non-resident-to-resident conversion is attempted for zero-size eligible attributes, with special protection for `$MFT/$BITMAP` and no support for compressed/encrypted conversion.
- Attribute insertion first tries the base MFT record, then existing extents, then creates an attribute list and/or allocates a new extent record. Resident and non-resident record creation update `$ATTRIBUTE_LIST` when present.
- Mapping-pairs update rewrites extents from a runlist, grows/shrinks mapping-pairs storage, may move attributes away, may create new extent records, and marks obsolete extents with `NTFS_VCN_DELETE_MARK` before removal.
- Sparse state is inferred from runlist holes. `ntfs_attr_update_meta()` adds/removes the `compressed_size` field space by moving names and mapping-pairs offsets when an attribute becomes or stops being sparse.
- Truncation paths split by resident/non-resident and grow/shrink. Non-resident growth may append holes for sparse-capable `$DATA` or allocate clusters; shrink frees clusters, truncates runlists, and updates mapping pairs.
- `ntfs_attr_map_cluster()` materializes an LCN for holes or delayed allocations, choosing a seek LCN from neighboring real runs, and either commits mapping pairs immediately or marks the runlist dirty.
- Range insertion/collapse/punch manipulate runlists with helper routines, adjust allocation/data/initialized sizes, update mapping pairs, free punched clusters, and mark filename metadata dirty where needed.
- `ntfs_attr_fallocate()` grows the unnamed data attribute if necessary, optionally restores visible size for keep-size mode, then allocates initialized-range holes and later uninitialized extents.

Important invariants:
- `ni->runlist.lock` must protect mutable runlists; mapping functions document read/write lock requirements.
- MFT records must be mapped/unmapped through search contexts or inode helpers, and dirty records must be marked after metadata changes.
- `$ATTRIBUTE_LIST` presence changes insertion/removal semantics; attribute-list entries must be kept sorted and synchronized with moved or deleted records.
- Attribute extents for a non-resident stream must advance monotonically by VCN and agree with the runlist after mapping-pairs rebuild.
- On-disk size fields, in-memory `allocated_size`, `data_size`, `initialized_size`, `i_blocks`, sparse/compressed flags, and filename dirty state must be updated together.
- Encrypted attributes are rejected by truncate/expand conversion paths; compressed truncation through `ntfs_attr_truncate_i()` is not supported.

Notable risks:
- This file contains many rollback paths where failures can leave leaked clusters or inconsistent metadata; several errors explicitly tell users to run `chkdsk`.
- `ntfs_attr_put_search_ctx()` unmaps `ctx->base_ntfs_ino` when `mapped_base_mrec` is set and current inode differs; this is delicate because external-search state distinguishes mapped base and mapped extent records.
- Some helpers return `-1` instead of a standard negative errno on internal failure, notably `ntfs_non_resident_attr_record_add()`, which callers treat as generic failure.
- `ntfs_non_resident_attr_insert_range()` leaks `hole_rl` on the early `ntfs_attr_map_whole_runlist()` error path after allocation.
- `ntfs_attr_map_cluster()` can defer mapping-pairs updates until low free space or later dirty-runlist flush, so callers must honor `NInoRunlistDirty`.
- Resident resize tries to free space by converting or moving unrelated attributes; this is powerful but increases the blast radius of one attribute resize.
- Range collapse can make an attribute resident when allocation reaches zero; callers need to tolerate representation changes.
