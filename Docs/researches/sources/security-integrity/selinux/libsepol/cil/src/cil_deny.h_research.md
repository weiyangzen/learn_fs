# sources/security-integrity/selinux/libsepol/cil/src/cil_deny.h

## Purpose
`cil_deny.h` declares the deny-rule processing interface and the class-permission list set operations used by deny handling and related code.

## Important APIs, Types, And Functions
The header exports match predicates `cil_classperms_list_match_any` and `cil_classperms_list_match_all`, structural copier `cil_classperms_list_copy`, set operations `cil_classperms_list_and` and `cil_classperms_list_andnot`, and the AST pass `cil_process_deny_rules_in_ast`.

## Control Flow
The header has no executable control flow. Consumers include it when they need permission-list intersection/difference semantics or the post-processing deny pass.

## State And Persistence Behavior
No state is owned here. Implementations allocate and destroy `struct cil_list` trees and may mutate the AST; callers must follow ownership conventions documented by the implementation.

## Dependencies And Integration Points
The declarations rely on forward-visible CIL types from internal headers, especially `struct cil_list` and `struct cil_db`. `cil_post.c` calls the deny pass, and `cil_deny.c` supplies the implementation.

## Risks And Edge Cases
Because the header does not include all type declarations itself, include order matters in consumers. The list operations return NULL for empty or invalid combinations in several cases, so callers must tolerate NULL and empty lists.

## Test Signals
Compile-time signals are missing prototypes or include-order regressions. Runtime signals come from deny-rule tests and direct tests of classpermission list copy/intersection/difference over plain classes, map classes, and classpermission sets.
