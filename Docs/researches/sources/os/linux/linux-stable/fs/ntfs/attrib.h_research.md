# File Research: sources/os/linux/linux-stable/fs/ntfs/attrib.h

Purpose: Public interface and shared structures for NTFS attribute handling.

Key contents:
- Declares `AT_UNNAMED`.
- Defines `struct ntfs_attr_search_ctx`, the state object used by attribute lookup and enumeration.
- Defines hole expansion policy enum: `HOLES_NO` and `HOLES_OK`.
- Declares runlist mapping, VCN lookup, attribute lookup, search-context lifecycle, size bounds, record resize, resident value resize, resident/nonresident conversion, truncate/expand/fallocate, range mutation, add/remove/existence, attrlist-sensitive record moves, name conversion, read-all, and mapping-pair update APIs.
- Provides `ntfs_attr_size()` inline helper to return resident value length or nonresident data size.
- Provides `ntfs_attrs_walk()` inline enumeration helper over `ntfs_attr_lookup(AT_UNUSED, ...)`.

Important invariants:
- `ntfs_attr_search_ctx` carries both current and base MFT-record state so callers can traverse attributes split across extent records.
- Callers using lookup/enumeration must preserve and release search contexts correctly because contexts can map MFT records.
- Header exposes several low-level mutation APIs, so locking requirements are documented mainly in `attrib.c` rather than enforced by the type system.

Dependencies:
- Includes `ntfs.h` and `dir.h`.
- Tightly coupled to MFT record layout, attribute-list entries, and runlist structures.
