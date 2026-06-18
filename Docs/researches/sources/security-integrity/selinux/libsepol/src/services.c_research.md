# sources/security-integrity/selinux/libsepol/src/services.c

## Purpose
`services.c` implements libsepol security services over a global active `policydb_t` and `sidtab_t`: access-vector computation, transition SID computation, context/SID conversion, policy reload, object SID lookup, user SID enumeration, and common policy-file read/write primitives.

## Important APIs and Control Flow
State setters install or load the active policydb/SID table. Access APIs compute decisions by resolving SIDs, scanning type-attribute combinations in `te_avtab`, applying conditional decisions, evaluating constraints/MLS constraints, checking process role transitions, and applying type-bound masking. SID derivation APIs build a new context from default rules, type transition/member/change rules, role transitions, MLS computation, context validity, and SID interning. Object lookup APIs resolve filesystem, port, netif, node, genfs, fs_use, InfiniBand pkey, and endport SIDs.

## State and Persistence
The service layer uses static defaults `mypolicydb` and `mysidtab` with global pointers, so it is process-global. `sepol_load_policy()` reads a new policy from memory, verifies class/permission compatibility, clones and converts existing SIDs, swaps active state, and frees old state. Object context lookups cache generated SIDs in `ocontext_t->sid[]`. `next_entry()`, `put_entry()`, and `str_read()` are the shared binary policy I/O helpers.

## Dependencies and Integration
The file depends on policydb, sidtab, avtab, conditional policy, context conversion, MLS helpers, Flask constants, and `private.h`. It bridges `policydb_read()`/`policydb_write()` with `struct policy_file`.

## Risks and Test Signals
Global state and reason-buffer globals are not thread-isolated. Unknown SIDs can remap to unlabeled. `str_read()` assigns the allocated string before a read failure, so caller ownership must be careful. Tests should cover reason-buffer resizing, invalid class/permission conversion, policy reload compatibility failures, memory-backed short I/O, object SID caching, IPv4/IPv6 matching, and enforcing/permissive invalid-context behavior.
