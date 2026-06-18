# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_btree.h

This header defines HAMMER’s on-disk B-Tree element and node structures, localization constants, element type constants, capacity constants, and small helper predicates. It documents HAMMER’s modified B+Tree design: records live only in leaves, while internal nodes include built-in left/right boundary information.

Key structures:
- `hammer_base_elm`: common key and type prefix for all B-Tree elements. Sort priority is localization, object id, record type, key, and create TID. It also stores delete TID, object type, element type, and localization.
- `hammer_btree_internal_elm`: base element plus mirror TID and subtree offset.
- `hammer_btree_leaf_elm`: base element plus create/delete timestamps, data offset, data length, and data CRC.
- `hammer_btree_elm`: union overlay for base, internal, and leaf element views.
- `hammer_node_ondisk`: 4 KB on-disk node containing CRC, parent pointer, count, node type, mirror TID aggregator, reserved fields, and 63 element slots.

Localization:
- Lower 16 bits encode localization type, including inode and misc.
- Upper 16 bits encode pseudo-filesystem id.
- Helper macros convert between localization and PFS id.
- The root inode uses the default localization.

Element and node constants:
- B-Tree element/node types include internal, leaf, record, deleted, and none.
- Leaf nodes hold 63 elements.
- Internal nodes logically hold one fewer element because the final physical element is a right boundary.
- `HAMMER_BTREE_CRCSIZE` excludes the CRC field itself.

Inline helpers:
- `hammer_is_internal_node_elm()` identifies internal-node child references.
- `hammer_is_leaf_node_elm()` identifies leaf record elements.
- `hammer_node_max_elements()` returns type-specific node capacity.
- `hammer_elm_btype()` maps element type to printable characters, including fallbacks for none and unknown types.

Architectural role:
- This header is included through HAMMER disk/internal headers and underpins all B-Tree search, update, CRC, mirror, and cursor logic.
- It is an on-disk ABI definition; layout changes affect filesystem compatibility.
