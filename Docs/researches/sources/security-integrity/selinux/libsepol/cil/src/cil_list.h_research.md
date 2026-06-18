# sources/security-integrity/selinux/libsepol/cil/src/cil_list.h

## Purpose
`cil_list.h` declares the generic CIL linked-list structure, iteration macros, and list helper APIs.

## Important APIs, Types, And Functions
It defines `struct cil_list` with `head`, `tail`, and list flavor, and `struct cil_list_item` with `next`, item flavor, and data pointer. Macros are `cil_list_is_empty` and `cil_list_for_each`. Functions mirror the implementation in `cil_list.c`.

## Control Flow
The header contributes macro-based iteration. `cil_list_for_each` assumes a non-NULL list pointer; callers must guard NULL lists themselves unless the local contract guarantees presence.

## State And Persistence Behavior
No state is stored here. The structs define heap-owned in-memory list topology used across AST and expression data.

## Dependencies And Integration Points
It includes `cil_flavor.h` and is consumed by parser, AST build, post-processing, deny processing, find logic, and policy emitters.

## Risks And Edge Cases
The iteration macro is unsafe with NULL lists and with mutation of the current item unless the caller stores `next` separately. The list flavor is advisory; many operations do not enforce it.

## Test Signals
Compile and sanitizer tests should exercise list operations through high-level policy parsing plus focused unit tests for insertion/removal and nested destruction.
