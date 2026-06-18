# sources/test-tools/strace/src/trie.h

Purpose: public interface and configuration structure for the sparse trie.

Important APIs/types/functions: `struct trie` fields for empty/fill value, root data pointer, key size, item width log2, node key bits, data-block key bits, and max depth; `trie_create`, `trie_set`, `trie_get`, `trie_iterate_fn`, `trie_iterate_keys`, and `trie_free`.

Control flow: callers create a configured trie, set/get key values, iterate inclusive ranges with a callback, and free ownership.

State and persistence behavior: documents heap-owned mutable trie state. No thread-safety guarantees.

Dependencies and integration points: includes `<stdbool.h>` and `<stdint.h>`; implemented by `trie.c`.

Risks: API does not expose allocation failures from `trie_set` beyond `false`; no resizing or defragmentation; caller must call `trie_free`.

Test signals: compile API users, ownership/free behavior, callback invocation count, and documented unsupported resizing behavior.
