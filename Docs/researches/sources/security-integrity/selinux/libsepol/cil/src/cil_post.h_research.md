# sources/security-integrity/selinux/libsepol/cil/src/cil_post.h

## Purpose
`cil_post.h` declares post-processing and context-rule comparator APIs used after CIL AST construction.

## Important APIs, Types, And Functions
It declares comparators for filecon, ibpkeycon, portcon, genfscon, netifcon, ibendportcon, nodecon, and fsuse records, plus `cil_post_process`.

## Control Flow
The header has no executable flow. The implementation sorts/deduplicates context arrays and orchestrates the complete post-processing pipeline.

## State And Persistence Behavior
No state is stored here. `cil_post_process` mutates the supplied `struct cil_db` by resolving expressions, filling arrays, processing deny rules, and setting policy defaults.

## Dependencies And Integration Points
It includes `cil_internal.h` and is consumed by `cil.c`, policy generation, tests, and any code that needs the canonical sort order for context records.

## Risks And Edge Cases
Comparator behavior must stay synchronized with kernel/libsepol expectations for context ordering. Calling `cil_post_process` more than once on the same database can be risky because many fields are allocated or transformed in place.

## Test Signals
Comparator unit tests should assert ordering for regex filecons, wildcard netifcons, ranges, IPv4/IPv6 nodecons, and duplicate handling. Full post-process integration tests should assert successful compilation and expected diagnostics for conflicts.
