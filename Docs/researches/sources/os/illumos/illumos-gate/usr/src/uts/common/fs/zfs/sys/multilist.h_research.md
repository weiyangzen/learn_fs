# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/multilist.h

This header declares `multilist_t`, a sharded list abstraction used to reduce lock contention while preserving normal list semantics within each sublist.

Core definitions:
- `multilist_node_t` aliases `list_node_t`; callers embed it in listed objects.
- `multilist_sublist_t` contains a per-sublist mutex, illumos `list_t`, and cache-line padding.
- `multilist_t` records the embedded-node offset, sublist count, sublist array, and caller-supplied object-to-sublist index function.
- Whole-list APIs create/destroy, insert/remove, test emptiness, expose sublist count, and choose a random sublist.
- Sublist APIs explicitly lock by index or object, insert/remove/move entries, and traverse head/tail/next/prev.

Risk-sensitive invariants:
- The index function must be stable while an object is inserted if callers use whole-list remove.
- Traversal safety is per-sublist; there is no single global lock for a consistent whole-list snapshot.
- Direct sublist APIs require callers to hold and release the matching sublist lock correctly.
