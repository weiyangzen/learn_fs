# sources/sync-backup/unison/src/hash_compat.c

Purpose: preserved pre-OCaml-4 universal hash implementation for Unison archive/version compatibility.

Important API: `unsn_hash_univ_param(count, limit, obj)` initializes `hash_state`, recursively hashes an OCaml value with historical `Alpha` and `Beta` combine constants, and returns a positive 30-bit value stable across 32/64-bit architectures.

Control flow: `hash_aux` decrements traversal limits, handles immediate ints, non-heap pointers, strings, doubles, double arrays, abstract/infix/forward/object/custom blocks, closure blocks under `NO_NAKED_POINTERS`, and generic blocks recursively.

State/persistence: no external state. The persistence concern is semantic: hash output affects compatibility with stored archives or protocols.

Dependencies/integration: OCaml runtime internals and tags. Comments warn removal will break Unison version compatibility and must wait for long user upgrade windows.

Risks: depends on OCaml runtime representation details. Compatibility value is high, so refactoring or replacing it can silently invalidate archives or cross-version behavior. Naked-pointer/no-naked-pointer runtime differences are explicitly conditional.

Test signals: regression vectors comparing known OCaml values to historical hash results on 32-bit/64-bit and old/new compiler configurations.
