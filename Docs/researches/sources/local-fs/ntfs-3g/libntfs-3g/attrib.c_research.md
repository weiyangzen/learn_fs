# File Research: sources/local-fs/ntfs-3g/libntfs-3g/attrib.c

## Scope

Implements NTFS attribute handling for libntfs-3g: opening attributes, resolving attribute-list extents, mapping VCNs to LCNs, reading/writing resident and non-resident data, resizing/truncating attributes, converting residency, updating mapping pairs, adding/removing attribute records, and validating on-disk attribute structure.

## API And Behavior

- Exports special NTFS Unicode names/constants: `AT_UNNAMED`, `STREAM_SDS`, and `TXF_DATA`.
- Attribute flag helpers expose compressed/encrypted/sparse state, but only allow inode file-attribute flag changes for unnamed `$DATA`.
- `ntfs_get_attribute_value_length()` and `ntfs_get_attribute_value()` read raw attribute values from an `ATTR_RECORD`; non-resident reads decompress mapping pairs and read clusters directly, with explicit limitations around compressed/sparse data and attribute lists.
- `ntfs_attr_open()` allocates and initializes `ntfs_attr`, validates names and flags, handles empty-stream compression policy, initializes resident/non-resident sizes, rejects unsupported compression units, and enforces consistency between unnamed `$DATA` flags and inode flags.
- `ntfs_attr_close()` releases runlists and dynamically duplicated names while preserving internal constant names.
- Runlist helpers include `ntfs_attr_map_runlist()`, optional `ntfs_attr_map_partial_runlist()`, `ntfs_attr_map_whole_runlist()`, `ntfs_attr_vcn_to_lcn()`, and `ntfs_attr_find_vcn()`. They lazily decompress mapping pairs, handle attribute extents, detect corrupt attribute lists, and mark fully mapped attributes.
- `ntfs_attr_pread()` reads resident values from MFT records or non-resident data through runlists. It zero-fills holes/uninitialized ranges, supports compressed reads only through `ntfs_compressed_attr_pread()`, denies encrypted non-resident reads unless `efs_raw` is enabled, and adds raw-EFS padding bytes in raw mode.
- `ntfs_attr_pwrite()` writes resident data into the MFT record or non-resident data through runlists. It extends attributes when needed, fills gaps with zeroes, allocates holes, supports compressed write paths one compression block at a time, updates mapping pairs, and attempts rollback of data/initialized sizes on failures.
- `ntfs_attr_pclose()` finalizes compressed non-resident attributes by compressing the terminal block and updating mapping pairs.
- `ntfs_attr_mst_pread()` and `ntfs_attr_mst_pwrite()` wrap attribute I/O with multi-sector transfer fixup/deprotect logic for records protected by NTFS update sequence arrays.
- `ntfs_attr_lookup()` dispatches to `ntfs_attr_find()` for single-record searches or `ntfs_external_attr_find()` when an attribute list is present. It supports enumeration with `AT_UNUSED`, insertion positioning on `ENOENT`, named/unnamed matching, value matching for resident attributes, and extent lookup by `lowest_vcn`.
- `ntfs_attr_inconsistent()` performs structural checks on resident and non-resident attributes and hard-coded well-known attribute constraints for file names, index roots, standard information, object IDs, volume attributes, and index allocation.
- Attribute definition helpers enforce `$AttrDef` size bounds, non-residency permission, resident permission, and special-case Windows compatibility rules such as resident `$LOGGED_UTILITY_STREAM:$TXF_DATA`.
- Record mutation helpers include `ntfs_make_room_for_attr()`, resident/non-resident record adders, `ntfs_attr_record_rm()`, `ntfs_attr_add()`, `ntfs_attr_set_flags()`, `ntfs_attr_rm()`, `ntfs_attr_record_resize()`, `ntfs_resident_attr_value_resize()`, and record movement between MFT extents.
- Residency conversion helpers convert resident attributes to non-resident records, force non-residency, convert non-resident attributes back to resident when allowed, and may move other attributes or create attribute lists to free MFT record space.
- `ntfs_attr_update_mapping_pairs()` rewrites mapping pairs from in-memory runlists, updates sparse/compressed metadata, adds/removes attribute extents, and can allocate new MFT records for overflow mapping pairs.
- Truncation paths shrink or expand resident and non-resident attributes, create holes for NTFS 3+ `$DATA`, avoid holes in solid truncation, maintain file-name/index size metadata, and special-case compressed files.
- Convenience helpers read/write data streams, shrink data size without freeing allocation, check/remove attribute existence, and count free bits in bitmap attributes.

## State And Dependencies

The file is the central coordinator between `ntfs_attr`, `ntfs_inode`, `MFT_RECORD`, `ATTR_RECORD`, attribute lists, runlists, cluster allocation, compression, MST fixups, volume geometry, `$AttrDef`, and device I/O. It depends heavily on endian conversions, MFT dirty flags, runlist sentinels (`LCN_HOLE`, `LCN_RL_NOT_MAPPED`, `LCN_ENOENT`), and inode state flags such as `NInoAttrList`, `NAttrRunlistDirty`, `NAttrFullyMapped`, `NAttrDataAppending`, and `NAttrBeingNonResident`.

## Risks And Invariants

Many operations mutate several structures that must stay synchronized: runlists, mapping pairs, allocated/data/initialized/compressed sizes, sparse/compressed flags, attribute-list entries, MFT record layout, and filename/index cached sizes. The code contains explicit partial-failure warnings where rollback is incomplete and metadata may be left inconsistent, especially around bitmap/runlist updates, mapping-pair rebuilds, resident/non-resident conversion, cluster freeing, and compressed writes. Encrypted non-resident attributes are mostly unsupported outside raw EFS mode. Compressed writes are constrained to supported NTFS compression mode and often one compression block at a time. Updating mapping pairs from nonzero `from_vcn` has documented sparse/compressed-size limitations.
