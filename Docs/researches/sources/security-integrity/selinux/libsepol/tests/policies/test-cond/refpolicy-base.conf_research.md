# sources/security-integrity/selinux/libsepol/tests/policies/test-cond/refpolicy-base.conf

## Purpose
This is the full reference-policy-like base fixture consumed by `test-cond.c`. It gives the conditional-expression tests a realistic base module containing kernel and userspace object classes, initial SIDs, a large MLS lattice, constraints, booleans, users, roles, types, and many conditional rules.

## Important APIs, Types, And Functions
The file is policy language, not C, but its important symbols are object classes such as `file`, `process`, sockets, X classes, and `dbus`; SIDs such as `kernel`, `security`, and `devnull`; categories `c0` through `c255`; booleans such as `allow_ypbind`, `secure_mode`, and `allow_execstack`; and policy constructs such as `mlsconstrain`, `if (...) { allow ... }`, `gen_user`, `gen_context`, `fs_use_xattr`, and `genfscon`.

## Control Flow
`cond_test_init()` loads this base with MLS enabled, links it as a base module, expands it, then walks `base_expanded.cond_list`. The control-flow signal in this fixture is its conditional policy tree: each `if` expression becomes a `cond_node_t`, and the test compares each node to every other node with `cond_expr_equal()`.

## State And Persistence Behavior
The fixture is parsed into a `policydb_t`, linked in place, then expanded into a second `policydb_t`. No runtime state is persisted by the policy file itself, but its symbols populate global symbol tables, scope tables, conditional nodes, MLS tables, context tables, and access-vector rules.

## Dependencies And Integration Points
It depends on the m4-style policy parser support used by `test_load_policy()`, including `ifdef(enable_mls, ...)`, `gen_user`, and `gen_context`. Its integration points are `link_modules()`, `expand_module()`, and the conditional-expression equality implementation.

## Risks And Edge Cases
Because the fixture is large, removing apparently unused classes, categories, or booleans can change condition node ordering or expression identity. The test only asserts equality against self and inequality against distinct nodes; it does not assert semantic equivalence for differently shaped expressions that evaluate the same way.

## Test Signals
Successful load, link, expand, and a populated `cond_list` are the main signals. A regression in conditional parsing, expression allocation, or expansion should surface as `cond_expr_equal()` returning true for distinct nodes or false for the same node.
