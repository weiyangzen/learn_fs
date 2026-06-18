# sources/security-integrity/selinux/libsepol/src/avtab.c

Purpose: Implements the access-vector table hash structure and binary policy AVTAB reader.

Important APIs and functions: `avtab_init`, `avtab_alloc`, `avtab_insert`, `avtab_insert_nonunique`, `avtab_search`, `avtab_search_node`, `avtab_search_node_next`, `avtab_destroy`, `avtab_map`, `avtab_hash_eval`, `avtab_read_item`, and `avtab_read`.

Control flow: Keys hash via a MurmurHash3-derived mix of class/target/source. Buckets are sorted by source, target, class. Normal insert rejects duplicate non-xperm keys; nonunique insert supports conditionals. Read code handles old and new binary formats, validates specifier masks, version-gates xperms, decodes little-endian data, and inserts each item.

State and persistence: `avtab_t` owns bucket arrays and nodes. Nodes optionally own `avtab_extended_perms_t`. Binary read populates persistent policydb AV tables.

Dependencies and integration points: Used by policydb reading, expansion, conditionals, assertions, and services.

Risks: Duplicate/specifier handling and xperm allocation are correctness hot spots. Malformed binary input must not overread or allocate excessive buckets.

Test signals: Binary policies across AVTAB versions, duplicate entries, xperms, zero/saturated counts, and lookup ordering validate it.
