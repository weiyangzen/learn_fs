# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_cache.c

Canonical-form cache and AST utility module for the LTL translator.

Key responsibilities:
- Caches formula rewrites from input AST (`before`) to canonical AST (`after`) to avoid repeated normalization.
- Allocates, duplicates, compares, and releases `Node` trees.
- Implements structural and algebraic equality checks, including commutative equality for right-linked AND/OR trees.
- Provides `anywhere` helpers for containment checks in AND/OR contexts.

Important functions:
- `cached`, `in_cache`: cache lookup/store around `Canonical`.
- `tl_nn`, `getnode`, `dupnode`, `releasenode`: AST allocation and lifecycle.
- `sameform`, `isequal`, `ismatch`: increasingly strict/equivalence-aware comparisons.
- `any_term`, `any_and`, `any_lor`, `anywhere`: formula containment queries used by rewrite and automaton logic.

Notable details:
- A `NULL` node can compare equal to `TRUE` in `isequal`, matching translator conventions.
- Cache returns duplicates of stored canonical forms to avoid accidental mutation of cached objects.

Risks/quirks:
- Memory is managed through translator pool allocator `tl_emalloc`/`tfree`.
- Equality logic depends on right-linked AND/OR normalization for full effectiveness.
