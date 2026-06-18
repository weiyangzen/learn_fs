# sources/security-integrity/selinux/libsepol/include/sepol/policydb/ebitmap.h

Purpose: Defines extensible bitmaps used for sets of types, roles, categories, classes, permissions, and scopes.

Important APIs and types: `ebitmap_node_t`, `ebitmap_t`, iterator macros, bit tests, and operations for compare, union, and/or/xor/not/andnot, cardinality, distance, copy, contains, match_any, get/set bit, range initialization, highest-set-bit, destroy, and binary read.

Control flow: Bitmaps are sparse linked lists of 64-bit map nodes with explicit start bits. Iterator macros walk all or positive bits.

State and persistence: Nodes are heap allocated and owned by the containing ebitmap. Many policydb structures serialize these sets.

Dependencies and integration points: Used across MLS, type/role sets, scope indexes, constraints, policy capabilities, and context validation caches.

Risks: Highbit/startbit invariants and sparse-node allocation are critical. Maxbit parameters for complement operations prevent accidental infinite universes.

Test signals: Sparse high-bit sets, range operations, contains/match_any, copy/destroy, and binary read of malformed bitmaps validate behavior.
