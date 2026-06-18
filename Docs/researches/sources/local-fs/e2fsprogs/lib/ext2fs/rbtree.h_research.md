# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/rbtree.h

Header for the namespaced red-black tree support. It defines `struct rb_node`, `struct rb_root`, color constants, parent/color accessors, empty-node helpers, `RB_ROOT`, `ext2fs_rb_entry`, and function prototypes.

The parent pointer and color bits are packed into `uintptr_t rb_parent_color`; the struct is aligned to `sizeof(long)` to preserve low bits for flags.

The header emphasizes that callers provide search and ordered insertion logic themselves, then call `ext2fs_rb_insert_color()` for balancing.
