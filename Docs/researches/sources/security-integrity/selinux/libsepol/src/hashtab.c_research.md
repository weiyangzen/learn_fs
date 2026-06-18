# sources/security-integrity/selinux/libsepol/src/hashtab.c

Purpose: implements libsepol's generic chained hash table used by policydb symbol tables and auxiliary maps. Buckets are sorted by caller-provided comparison to support deterministic lookup traversal within chains.

Important APIs and functions: `hashtab_create` allocates a table with caller-supplied hash and compare callbacks. `hashtab_insert`, `hashtab_remove`, `hashtab_search`, `hashtab_destroy`, and `hashtab_map` provide core operations. `hashtab_check_resize` doubles the bucket array when element count reaches size. `hashtab_hash_eval` prints bucket statistics for diagnostics.

Control flow: insertion resizes if needed, hashes the key, walks the sorted chain until an equal or larger key, rejects duplicates, and splices a new node. Resize rehashes every node into a new bucket array while preserving sorted-chain insertion. Removal/search use the sorted chain to stop early when comparison passes the target. Map iterates bucket order and stops on first non-zero callback result.

State and persistence behavior: table state is heap-resident only. The table owns nodes and bucket arrays, but key and datum ownership is external unless `hashtab_remove` is supplied a destroy callback. `hashtab_destroy` frees nodes only, not pointed-to keys/data.

Dependencies and integration points: depends on public hashtab types and `private.h` error constants. Used pervasively for policydb symbol tables, range transitions, filename transitions, and generated string maps.

Risks: resize silently keeps the old table if allocation fails, which preserves correctness but may degrade performance. Callers must keep hash callbacks valid after `h->size` changes because hash values are bucket indexes. `hashtab_destroy` not freeing keys/data is a common ownership trap. `hashtab_hash_eval` prints directly to stdout and uses `%d` for unsigned table fields.

Test signals: insert/search/remove duplicates and ordered keys, resize boundaries including overflow guard at `UINT32_MAX`, map early exit, destroy ownership expectations, hash distribution diagnostics, and allocation-failure behavior during resize and node allocation.
