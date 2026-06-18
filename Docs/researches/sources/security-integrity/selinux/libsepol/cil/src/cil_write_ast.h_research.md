# sources/security-integrity/selinux/libsepol/cil/src/cil_write_ast.h

## Purpose
`cil_write_ast.h` exposes the CIL AST writer interface used by code that needs to dump parse/build/resolve/post AST state to a `FILE *`. It is the small public contract for `cil_write_ast.c`.

## Important APIs, Types, And Functions
The header defines `enum cil_write_ast_phase` with `CIL_WRITE_AST_PHASE_PARSE`, `CIL_WRITE_AST_PHASE_BUILD`, `CIL_WRITE_AST_PHASE_RESOLVE`, and `CIL_WRITE_AST_PHASE_POST`. It declares `void cil_write_ast_node(FILE *out, struct cil_tree_node *node)` for one-node serialization and `int cil_write_ast(FILE *out, enum cil_write_ast_phase phase, struct cil_tree_node *node)` for whole-tree traversal.

## Control Flow
This header contains no executable flow. Its enum values drive the branch in `cil_write_ast()` that selects parse-tree callbacks versus semantic CIL callbacks.

## State And Persistence
No state is stored here. Callers provide the output stream and tree node. The implementation writes to the stream and returns `SEPOL_OK`/`SEPOL_ERR` for whole-tree operations.

## Dependencies And Integration Points
The header includes `<stdio.h>` for `FILE` and `cil_tree.h` for `struct cil_tree_node`. Any caller including this file gets the AST writer phase enum and can request dumps without depending on private serializer helpers.

## Risks
The enum is an ABI/API coordination point with the implementation. Adding a new phase requires corresponding behavior in `cil_write_ast.c`; otherwise it will use the non-parse path. The header does not document ownership, null handling, or output syntax guarantees, so callers must follow implementation conventions.

## Test Signals
Compile-time coverage comes from any CIL component or test harness that includes the header. Functional validation depends on tests that call `cil_write_ast()` and verify emitted text.
