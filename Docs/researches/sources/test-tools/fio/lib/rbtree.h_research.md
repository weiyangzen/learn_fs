# sources/test-tools/fio/lib/rbtree.h

Purpose: declares intrusive red-black tree data structures and helper macros.

Important APIs/types: `struct fio_rb_node`, `struct rb_root`, color/parent macros, `RB_ROOT`, `rb_entry`, empty/clear helpers, `rb_insert_color`, `rb_erase`, `rb_first`, `rb_next`, and `rb_link_node`.

Control flow/state: callers embed `fio_rb_node`, maintain search/insert order, link a red node, rebalance, and erase/traverse as needed. Parent pointer and color share low bits in `rb_parent_color`.

Dependencies/integration: uses `container_of`, expected from fio/linux-style headers. Alignment is set to `sizeof(long)` to preserve low pointer bits.

Risks/test signals: nodes must be aligned and initialized/cleared before empty-node checks. Tests should cover embedding through `rb_entry` and parent/color bit packing on supported architectures.
