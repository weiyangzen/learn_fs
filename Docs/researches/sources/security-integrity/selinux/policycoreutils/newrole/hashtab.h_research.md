<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/hashtab.h -->
# sources/security-integrity/selinux/policycoreutils/newrole/hashtab.h

## Purpose

Public contract for the newrole generic hash table implementation. The source was read completely for this report (115 lines).

## Important APIs, Types, and Functions

Defines generic key/datum typedefs, node/table structs, status macros (`HASHTAB_SUCCESS`, `HASHTAB_OVERFLOW`, `HASHTAB_PRESENT`, `HASHTAB_MISSING`), and prototypes for create/insert/remove/search/destroy/map/hash-eval.

## Control Flow

No executable flow; it describes callback-driven hashing/comparison and table operations implemented in `hashtab.c`.

## State and Persistence Behavior

The table struct exposes bucket array, size, element count, and callbacks, so callers can inspect but should avoid mutating internals outside the implementation contract.

## Dependencies and Integration Points

Depends on stdint/errno/stdio and pairs directly with `hashtab.c`.

## Risks and Edge Cases

Risks are ABI drift with `hashtab.c`, exposed internals enabling misuse, and generic `char *` key typing that may not fit all callers.

## Test Signals

Compile coverage and hashtab operation tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/hashtab.h -->
