# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/btree.h

Defines the core on-disk and in-memory btree/recno data model. Page zero is metadata, page one is root, and `PAGE` headers carry page number, sibling links, flags, and line-pointer bounds. Page variants include btree internal (`BINTERNAL`), btree leaf (`BLEAF`), recno internal (`RINTERNAL`), recno leaf (`RLEAF`), and overflow pages.

The header defines alignment and sizing macros (`BTLALIGN`, `NBINTERNAL`, `NBLEAFDBT`, `NRLEAFDBT`), field writers (`WR_BINTERNAL`, `WR_BLEAF`, `WR_RINTERNAL`, `WR_RLEAF`), and accessors (`GETBINTERNAL`, `GETBLEAF`, `GETRINTERNAL`, `GETRLEAF`). It also defines `EPG`/`EPGNO` for pinned and unpinned page/index references.

`CURSOR` describes btree and recno cursor state, including deleted-cursor recovery flags. `BTMETA` is the disk metadata. `BTREE` holds the mpool handle, DB pointer, current and pinned pages, cursor, fixed-depth parent stack, return buffers, file descriptors, recno backing-file state, comparison/prefix callbacks, and flags for btree/recno behavior.

Dependencies are intentionally broad: this header includes `<mpool.h>` and `extern.h` and is the common contract for btree and recno implementation files.

Risks/invariants: structures must not be randomly padded because they are used as disk layouts. Many macros perform unaligned-looking casts that assume historical Berkeley DB layout constraints.
