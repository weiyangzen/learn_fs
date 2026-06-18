# sources/security-integrity/selinux/libsepol/src/ebitmap.c

Purpose: implements libsepol's sparse extensible bitmap abstraction used throughout policydb for type, role, user, category, capability, and rule-set membership. Bitmaps are stored as sorted linked nodes, each carrying a fixed-width machine map starting at `startbit`.

Important APIs and functions: set algebra includes `ebitmap_or`, `ebitmap_union`, `ebitmap_and`, `ebitmap_xor`, `ebitmap_not`, and `ebitmap_andnot`. Queries and utilities include `ebitmap_cardinality`, `ebitmap_hamming_distance`, `ebitmap_cmp`, `ebitmap_contains`, `ebitmap_match_any`, `ebitmap_get_bit`, and `ebitmap_highest_set_bit`. Mutators include `ebitmap_cpy`, `ebitmap_set_bit`, `ebitmap_init_range`, `ebitmap_destroy`, and `ebitmap_read`.

Control flow: algebra functions walk sorted node lists and allocate destination nodes only for non-empty maps. `ebitmap_set_bit` finds or creates the node for the requested bit, removes empty nodes when clearing, and updates `highbit` when the highest node changes. `ebitmap_read` reads map size, highbit, and node count from a little-endian policy stream, then validates alignment, ordering, non-zero node maps, bounds, and final highbit consistency.

State and persistence behavior: bitmap state is in caller-owned `ebitmap_t` node chains. `ebitmap_read` is the persistence boundary for binary policy input; it destroys partially built state on malformed or truncated input. Algebra functions usually initialize the destination and expect callers to destroy it.

Dependencies and integration points: depends on public policydb ebitmap structures, policy stream helpers in `private.h`, endian conversion, and `debug.h` diagnostics. It is foundational for expansion, MLS category handling, hierarchy checks, hashtab-to-string conversion, and kernel-to-CIL output.

Risks: ownership is manual and several functions return negative errno-style values while some callers collapse them to `-1`. `ebitmap_union` replaces `dst` through a temporary, so callers must not pass aliased inputs that violate expectations. `ebitmap_get_bit` tests `e->highbit < bit`, so edge behavior depends on the convention that `highbit` is one past the represented map boundary. Allocation failures in `ebitmap_init_range` can leak already-created nodes because it returns directly without destroying `e`.

Test signals: test sparse and dense OR/AND/XOR/NOT results, node deletion when clearing the last bit in a node, highbit updates, containment and any-match with disjoint starts, range initialization across one and multiple map nodes, binary read rejection for unsorted/zero/truncated/out-of-bounds maps, and memory-failure cleanup paths.
