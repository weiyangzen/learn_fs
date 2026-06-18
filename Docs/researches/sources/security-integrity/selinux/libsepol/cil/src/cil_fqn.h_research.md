# sources/security-integrity/selinux/libsepol/cil/src/cil_fqn.h

## Purpose
`cil_fqn.h` declares helpers for assigning and comparing fully qualified CIL symbol names.

## Important APIs, Types, And Functions
It declares `cil_fqn_qualify_blocks`, `cil_fqn_qualify`, `cil_fqn_qualify_all`, and `cil_fqn_compare`.

## Control Flow
The header has no executable flow. Implementations either qualify one datum using explicit block lists or node ancestry, or qualify all data in an AST.

## State And Persistence Behavior
No state is owned by the header. Implementations update `fqn` fields on existing datums and allocate interned strings.

## Dependencies And Integration Points
It includes `cil_internal.h` for `struct cil_db` and `struct cil_symtab_datum`. It is used by AST build and verification/output code needing stable display and comparison names.

## Risks And Edge Cases
Consumers must call qualification after enough AST parent/symtab information exists and before FQN-dependent sorting or output. Missing qualification can make later pointer comparisons against keyword strings or emitted names incorrect.

## Test Signals
Tests should check qualified names in nested scopes and stable compare ordering after qualification.
