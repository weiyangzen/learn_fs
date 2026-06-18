# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/sa_impl.h

This private header defines the in-memory and on-disk implementation details behind System Attributes.

Core definitions:
- `sa_attr_table_t` stores per-attribute ID, registration state, fixed length, byteswap class, and name.
- `ATTR_*` macros encode/decode persistent registry entries containing attr number, byteswap type, and length.
- `TOC_*` macros encode/decode per-layout table-of-contents entries: presence, variable-length index, and offset.
- `SA_LAYOUTS` and `SA_REGISTRY` name the ZAP objects used for persistent metadata.
- `sa_lot_t` is a layout table entry keyed by layout number and by hash, with ordered attributes, variable-size count, total attr count, and cached index tables.
- `sa_idx_tab_t` caches offsets for a layout and variable-length vector, with refcounted sharing across handles.
- `sa_os` stores objset-level SA state: locks, master/registry/layout objects, private attr table, layout AVL trees, update callback, and caller name-to-attr table.
- `sa_hdr_phys_t` is the bonus/spill header with magic, encoded layout number/header size, and optional variable-length array.
- `sa_handle` stores DB user data, handle lock, bonus/spill dbufs, objset, user pointer, and cached index tables.

Important macros and APIs:
- Header macros extract/set layout number, header size, and header layout info.
- Buffer macros select bonus vs spill dbufs, headers, and index tables.
- `SA_LAYOUT_NUM()` maps legacy non-SA or zero-layout cases to layout conventions.
- Internal helpers include `sa_add_impl()`, update callback registration, locked size query, default locator, and attribute-size lookup.

Risk-sensitive invariants:
- `SA_MAGIC`, layout numbers, registry encoding, and header-size encoding are on-disk format.
- Variable-length attributes require matching header-size and layout metadata.
- Index tables are shared with refcounts; handle rebuild/destruction must balance holds.
- Legacy non-SA bonus types map through special layout logic and cannot be treated as normal SA headers.
