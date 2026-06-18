# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen4.h

This header embeds the minimized-automaton (`MA`) runtime used by generated verifiers for graph-encoded state storage.

Key contents:
- `Dfa[]`: generated C code included when `MA` is defined.
- Defines `Edge` and `Vertex` structures for a layered DFA over byte-valued state-vector symbols.
- Maintains `layers`, `path`, root/final/non-final vertices, free lists, cached words, and counters.
- Implements edge insertion/removal, vertex recycling, transition lookup, key generation, splay-tree storage, DFA initialization, membership, insertion, and statistics.

Important details:
- The DFA represents state sets compactly with shared suffix/prefix structure and minimized transitions.
- Each vertex stores two inline transition ranges plus a linked list for additional edges.
- `setDelta()` updates one byte transition while preserving and merging edge ranges/singletons.
- `dfa_store()` checks membership and inserts a new state vector by walking the previous word prefix, reusing existing vertices, splitting shared paths, and recycling unreachable vertices.
- `dfa_member()` tests whether a suffix path reaches the final vertex.
- `insert_it()`, `find_it()`, and `delete_it()` manage per-layer splay trees keyed by transition structure.
- `dfa_stats()` reports node and edge counts for the minimized automaton.
- The algorithm comments credit Anuj Puri, Gerard Holzmann, and earlier graph-encoded-set work.

Filesystem relevance:
- Indirect. This is in-memory state-storage compression for generated verifiers.
