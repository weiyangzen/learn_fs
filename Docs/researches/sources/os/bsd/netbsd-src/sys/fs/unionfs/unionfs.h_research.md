# File Research: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs.h

Read completely: 162 lines.

Defines the interface and private structures for the newer FreeBSD-derived `unionfs` implementation. It keeps the same `struct union_args` layout and `UNMNT_ABOVE`/`UNMNT_BELOW`/`UNMNT_REPLACE` flags, with `unionfs_args` aliased to `union_args`.

Kernel-only definitions add copy and whiteout policy enums: `UNIONFS_TRADITIONAL`, `UNIONFS_TRANSPARENT`, `UNIONFS_MASQUERADE`, plus `UNIONFS_WHITE_ALWAYS` and `UNIONFS_WHITE_WHENNEEDED`. `struct unionfs_mount` stores lower/upper roots, root union vnode, a lock, copy/whiteout modes, ownership/mode defaults, and mount ordering. `struct unionfs_node_status` tracks per-process/per-LWP open counts, lower open mode, and readdir phase. `struct unionfs_node` stores upper/lower vnode pointers, parent union vnode, back pointer, status list, saved path, and flags.

The header declares node management, per-thread status management, upper attribute creation, copy-up, shadow directory/whiteout creation, relookup helpers, rmdir checks, diagnostic vnode accessors, vnode operation vector pointer, and malloc type declarations. Debug printing is enabled through `UNIONFS_DEBUG`.

Risks and notes: the include guard is the same as legacy `union/union.h`, so both headers conflict. `UNIONFS_DEBUG` is defined unconditionally, making `UNIONFSDEBUG()` expand to `printf()`. The public install path/name overlaps the legacy union filesystem.
