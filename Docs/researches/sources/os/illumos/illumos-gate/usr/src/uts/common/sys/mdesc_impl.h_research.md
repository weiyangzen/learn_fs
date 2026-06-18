# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mdesc_impl.h

Purpose: Defines internal representation and byte-order helpers for machine descriptions.

Key structures:
- `md_header_t`: transport version and byte sizes for node, name, and data blocks.
- `md_element_t`: 16-byte element with tag, name metadata, and value/data/arc union.
- `md_impl_t`: parsed machine description session with allocator hooks, block pointers, sizes, counts, root node, generation, and magic value.

Key macros:
- `LIBMD_MAGIC`.
- `mdtoh*` and `htomd*` byte-order conversions; machine descriptions are stored in network byte order.
- Accessors for element tag, name, property offsets/lengths, values, and indexes.

Key APIs:
- `md_ident_name_str()`
- `md_find_node_prop()`

Important detail: Elements are referenced by index derived from byte offset divided by 16, avoiding alignment-sensitive pointers into the node block.

Relevance to subset A: Virtualization/platform support internals.
