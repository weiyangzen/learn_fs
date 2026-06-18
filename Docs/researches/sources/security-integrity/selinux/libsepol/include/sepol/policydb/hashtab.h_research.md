# sources/security-integrity/selinux/libsepol/include/sepol/policydb/hashtab.h

Purpose: Declares the generic chained hash table used by policydb symbol tables and other mappings.

Important APIs and types: `hashtab_key_t`, `hashtab_datum_t`, `hashtab_node_t`, `hashtab_t`; create, insert, remove, search, destroy, map, and hash-evaluation functions.

Control flow: Callers provide hash and key comparison callbacks at create time, then insert/search/remove arbitrary key/datum pairs. `hashtab_map` stops and propagates nonzero callback results.

State and persistence: Tables own nodes but ownership of keys/data is controlled by caller destroy callbacks or surrounding symtab policy.

Dependencies and integration points: Included by `symtab.h` and many policydb internals.

Risks: Ownership is manual; mismatched key/data destroy behavior leaks or double-frees. Iteration order is bucket-dependent and not stable API.

Test signals: Duplicate insert, missing remove, map early error, destroy callbacks, and collision-heavy buckets validate behavior.
