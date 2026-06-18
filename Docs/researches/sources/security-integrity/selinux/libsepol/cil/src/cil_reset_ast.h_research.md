# sources/security-integrity/selinux/libsepol/cil/src/cil_reset_ast.h

## Purpose

`cil_reset_ast.h` declares the reset pass used to clear resolution-derived AST state before re-running resolver passes.

## Important APIs, Types, and Functions

The header includes `cil_tree.h` and exports `int cil_reset_ast(struct cil_tree_node *current);`. The parameter is the subtree root to reset; the return value follows libsepol `SEPOL_OK`/`SEPOL_ERR` conventions.

## Control Flow and Integration

Callers supply a resolved or partially resolved AST node. The implementation performs a depth-first tree walk and mutates nodes in place. The primary caller is the resolver when disabled optional blocks force declaration reset.

## State, Dependencies, and Risks

The API exposes no ownership details, so callers must know it preserves AST structure while clearing derived fields. It depends on `struct cil_tree_node` being visible. The main risk is calling it on a subtree that should retain resolution products; all supported CIL flavors under that subtree may have resolved pointers and derived lists cleared.

## Test Signals

Compile-time coverage should catch signature drift. Behavioral coverage belongs with resolver tests that trigger `cil_reset_ast()` and then successfully complete a second resolution pass.
