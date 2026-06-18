# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_deadlist.h

Read status: complete, 89 lines.

Purpose: persistent deadlist abstraction for blocks no longer referenced by a dataset but still relevant to snapshot lineage.

Key structures and APIs:
- `dsl_deadlist_phys_t` stores used/compressed/uncompressed totals and padding.
- `dsl_deadlist_t` stores objset/object, AVL tree, physical dbuf, lock, and old-format `bpobj_t`.
- `dsl_deadlist_entry_t` maps minimum TXG to a `bpobj_t`.
- APIs open/close/alloc/free, insert block pointers, add/remove TXG keys, clone up to a TXG, query total/range space, merge another deadlist, move a bpobj into the deadlist, and test open state.

Dependencies: `bpobj.h`, ZFS context, DMU objects/transactions.

Research notes:
- Supports both current tree-based format and old bpobj-only format.
- Used heavily by dataset snapshot/clone/destroy accounting.
