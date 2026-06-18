# File Research: sources/os/linux/linux/fs/xfs/scrub/attr.c

This file scrubs extended attribute metadata for an inode. It validates shortform attributes, attr leaf blocks, dabtree indexing, remote value retrieval, namespace flags, and parent pointer attribute values.

`xchk_setup_xattr_buf` manages reusable scrub scratch storage in `struct xchk_xattr_buf`: bitmaps for used/free bytes in attr blocks, an optional name buffer for repair, and a dynamically sized value buffer. `xchk_setup_xattr` invokes repair setup when possible, preallocates maximum buffers during try-harder retries, and then prepares inode content scrub locking.

For semantic validation, `xchk_xattr_actor` is called by xattr walking. It rejects unknown on-disk flags, marks incomplete attributes for preening, checks names with `xfs_attr_namecheck`, validates parent pointer values, allocates a buffer large enough for the value, and calls `xfs_attr_get_ilocked` after setting the hash to ensure the attribute can be found through normal lookup paths. Value length mismatches or lookup failures are flagged as corruption.

For physical layout validation, `xchk_xattr_set_map` tracks byte occupancy within shortform or leaf blocks and detects overlaps/out-of-range regions. `xchk_xattr_check_sf` walks shortform entries, validates entry bounds and legal flags, and marks header, entry, name, and value regions as used. Leaf-block checking validates padding, leaf header bounds, empty leaf cases, entry array placement, monotonic hash order, name/value storage bounds, local versus remote entry rules, freemap consistency, freemap/usedmap disjointness, and `usedbytes`.

`xchk_xattr_rec` ties the generic dabtree scrubber to attr-specific record validation by checking hash ordering and recomputing hashes for local and remote entries. Parent pointer attributes are not allowed to be remote in this logic. After physical checks pass, the scrubber performs a name/hash lookup pass over all attributes.
