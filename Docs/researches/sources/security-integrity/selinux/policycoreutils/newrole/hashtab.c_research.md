<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/hashtab.c -->
# sources/security-integrity/selinux/policycoreutils/newrole/hashtab.c

## Purpose

Standalone generic hash table implementation used by policycoreutils newrole PAM builds. The source was read completely for this report (205 lines).

## Important APIs, Types, and Functions

Implements `hashtab_create`, `hashtab_insert`, `hashtab_remove`, `hashtab_search`, `hashtab_destroy`, `hashtab_map`, and `hashtab_hash_eval`. The table uses creator-provided hash and comparison callbacks and ordered singly linked chains per bucket.

## Control Flow

Creation allocates the table and bucket array. Insert locates sorted position and rejects duplicate keys. Remove unlinks matching nodes and calls a caller-supplied destructor. Search walks the ordered chain. Map visits entries until callback failure. Destroy frees nodes and buckets but not key/datum payloads unless removed with a destructor earlier.

## State and Persistence Behavior

State is heap-owned `hashtab_val_t` with bucket chains and element count. Payload ownership remains with callers except for node storage.

## Dependencies and Integration Points

Depends only on libc allocation/string and `hashtab.h`; integrated into newrole when PAM support is present.

## Risks and Edge Cases

Risks include caller ownership mistakes for key/datum lifetimes, hash callbacks returning out-of-range bucket indexes, sorted-chain assumptions tied to `keycmp`, and no internal locking.

## Test Signals

Signals include insert/search/remove duplicate/missing cases, destructor invocation, map early return, destroy under empty/non-empty tables, and hash distribution diagnostics.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/hashtab.c -->
