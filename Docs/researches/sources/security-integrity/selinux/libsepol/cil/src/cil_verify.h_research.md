# sources/security-integrity/selinux/libsepol/cil/src/cil_verify.h

## Purpose

`cil_verify.h` declares the parser/resolver verification helpers and the argument structure used by verify tree walks.

## Important APIs, Types, and Functions

`enum cil_syntax` defines parse-node shape masks for strings, lists, empty lists, variadic lists/strings, and end-of-list. `struct cil_args_verify` carries `db`, an optional complex symtab, singleton-output pointers for `handleunknown` and `mls`, a `nseuserdflt` count pointer, and the active pass pointer. The header declares name, syntax, expression, constraint, conditional, macro-shadowing, range, ordering, SID, senscat, full verify helper, and pre-verify helper functions.

## Control Flow and Integration

Build/parsing code can use syntax helpers early, while compiler verification walks pass `cil_args_verify` to `cil_tree_walk()` with `__cil_pre_verify_helper()` or `__cil_verify_helper()`. Resolver code also calls `__cil_verify_ordered()` after ordered-list merging.

## State, Dependencies, and Risks

The header includes CIL internal, flavor, tree, and list definitions, binding it to internal compiler structures. The double-underscore function names are still externally declared, so they form a de facto internal API. Callers must initialize all pointer fields in `cil_args_verify` before walking.

## Test Signals

Tests should compile downstream users of the header and run tree-walk verification with both pass values. Syntax mask tests should confirm `CIL_SYN_N_LISTS` and `CIL_SYN_N_STRINGS` only accept homogeneous tails before `CIL_SYN_END`.
