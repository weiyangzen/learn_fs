# File Research: sources/os/bsd/freebsd-src/sys/sys/pctrie.h

This header defines a path-compressed trie interface used for keyed pointer/value indexing in the kernel. It includes private trie and SMR definitions, provides an iterator structure with reset/init helpers, and under `_KERNEL` declares generic trie functions plus macro generators for typed wrappers.

`PCTRIE_DEFINE` creates a type-safe family of inline functions for a containing structure whose embedded `uint64_t` field is the trie key/value anchor. It asserts field size and flag-bit alignment, converts between embedded value pointers and containing structures, and generates insert, find-or-insert, insert-with-lookup-LE, lookup, range lookup, LE/GE lookup, iterator lookup/stride/next/prev/value/jump/step, replace, remove, remove-lookup, reclaim, and reclaim-with-callback helpers. Allocation and free functions for internal nodes are supplied by the instantiating caller.

`PCTRIE_DEFINE_SMR` extends the generated API with unlocked lookup/range lookup under a provided SMR domain. Low-level functions implement insert lookup, node insertion, lookups, range scans, iterator movement, reclamation, removal, replacement, node sizing, and zone initialization.

The trie encodes leaves by setting low pointer bit `PCTRIE_ISLEAF`, with `PCTRIE_NULL` representing an empty leaf. Width is 4 on LP64 and 3 on 32-bit, chosen to keep child arrays cache-line friendly while relying on path compression. Filesystem/VM relevance is high: this kind of keyed sparse index is used for page, object, or other kernel maps where efficient ordered lookup and range scans matter.
