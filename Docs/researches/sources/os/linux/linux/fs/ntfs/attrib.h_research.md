# File Research: sources/os/linux/linux/fs/ntfs/attrib.h

Declares the NTFS attribute subsystem interface and the `ntfs_attr_search_ctx` state object used by lookup, mapping, mutation, and enumeration paths.

Key exports:
- `AT_UNNAMED` is the shared sentinel for unnamed attributes.
- `struct ntfs_attr_search_ctx` tracks current/base MFT records, current attribute record, mapped-record ownership, current attribute-list entry, and search continuation state.
- Runlist APIs include `ntfs_map_runlist_nolock()`, `ntfs_map_runlist()`, `ntfs_attr_vcn_to_lcn_nolock()`, `ntfs_attr_find_vcn_nolock()`, `__ntfs_attr_find_vcn_nolock()`, `ntfs_attr_map_whole_runlist()`, `ntfs_attr_vcn_to_rl()`, and `ntfs_attr_map_cluster()`.
- Lookup and context APIs include `ntfs_attr_lookup()`, `load_attribute_list()`, `ntfs_attr_reinit_search_ctx()`, `ntfs_attr_get_search_ctx()`, `ntfs_attr_put_search_ctx()`, and inline `ntfs_attrs_walk()`.
- Attribute sizing and representation APIs include `ntfs_attr_size()`, `ntfs_attr_size_bounds_check()`, `ntfs_attr_can_be_resident()`, `ntfs_attr_record_resize()`, `ntfs_resident_attr_value_resize()`, and `ntfs_attr_make_non_resident()`.
- Mutation APIs include add/remove/read-all/update-mapping-pairs/truncate/expand/fallocate/range insert-collapse-punch functions.

Core mechanics:
- `ntfs_attr_size()` abstracts resident value length versus non-resident data size.
- `ntfs_attrs_walk()` enumerates all attributes by calling `ntfs_attr_lookup(AT_UNUSED, ...)`.
- `HOLES_NO` and `HOLES_OK` define expansion policy for sparse holes.

Important invariants:
- Callers using `ntfs_attr_search_ctx` must account for context pointers moving after runlist mapping.
- Search contexts need explicit release with `ntfs_attr_put_search_ctx()`.
- The header exposes both low-level record edits and high-level operations, so call sites must respect locking comments in `attrib.c`.

Notable risks:
- The API surface is broad and low-level; misuse can bypass attribute-list synchronization, dirty marking, or runlist locking.
