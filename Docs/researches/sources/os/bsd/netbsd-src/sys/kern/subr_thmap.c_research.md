# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_thmap.c

Read completely: 1077 lines.

This file implements `thmap`, a concurrent trie-hash map. It stores entries in a radix trie over hashed keys: the root has 64 slots, subsequent internal nodes have 16 slots, and deeper levels derive more 32-bit hash material using a seeded BLAKE2s hash. The implementation supports lock-free readers, per-node writer locking, pointer tagging, offset-based pointers for shared-memory friendliness, and staged garbage collection.

Core design:
- Internal nodes (`thmap_inode_t`) contain an atomic state field with `NODE_LOCKED`, `NODE_DELETED`, and slot count bits.
- Leaves (`thmap_leaf_t`) store key offset/reference, key length, and value pointer.
- Pointers are offsets from `thmap->baseptr`; leaf pointers are tagged with bit 0.
- `THMAP_NOCOPY` stores caller-owned key references; otherwise keys are copied into thmap-allocated memory.
- Allocation is abstracted through `thmap_ops_t`, with kernel defaults using `kmem_intr_alloc/free`.

Key operations:
- `thmap_create`, `thmap_setroot`, `thmap_getroot`, and `thmap_destroy` manage map object/root setup.
- `thmap_get` initializes a hash query, descends without locking, validates the leaf key, and returns the value.
- `thmap_put` preallocates a leaf, tries a CAS root insertion, then locks edge nodes to insert or expand collision chains with internal nodes.
- `thmap_del` locks the edge node, removes matching leaves, collapses empty internal nodes upward, marks deleted nodes so readers restart/fail, clears empty root slots, and stages removed memory for GC.
- `thmap_stage_gc` atomically detaches the pending GC list; `thmap_gc` frees staged memory.

Concurrency/integration: root publication uses CAS/release semantics; readers use consume loads. Writers lock bottom-up and never mutate parent pointers after publication. Deleted nodes remain valid until the caller arranges reclamation by staging and later running GC, typically after an epoch or similar reader quiescence mechanism.

Reliability notes: `thmap_destroy` only drains staged GC and frees the root array when it owns it; callers must ensure live entries/nodes are gone or otherwise accounted for. Deep collision paths allocate one internal node per extra collision level. Correctness depends on external GC discipline: freeing staged nodes while lock-free readers can still observe them would be unsafe.
