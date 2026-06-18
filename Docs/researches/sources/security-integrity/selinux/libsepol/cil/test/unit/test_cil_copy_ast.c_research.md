# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_copy_ast.c

## Purpose
This file unit-tests CIL AST copy behavior. It verifies direct copy helpers for lists and individual CIL datum types, plus the internal `__cil_copy_node_helper` traversal path used to copy generated AST nodes into another destination tree or merge them into the same database.

## Important APIs, Types, And Functions
The file includes `CuTest.h`, `CilTest.h`, `cil_internal.h`, `cil_copy_ast.h`, `cil_build_ast.h`, and `cil_resolve_ast.h`. It forward-declares `__cil_copy_node_helper`, defines `struct cil_args_copy { struct cil_tree_node *dest; struct cil_db *db; }`, and provides `gen_copy_args`. Direct tests cover `cil_copy_list`, `cil_copy_block`, `cil_copy_perm`, `cil_copy_class`, `cil_copy_common`, `cil_copy_classcommon`, `cil_copy_sid`, `cil_copy_sidcontext`, user/role/type/boolean/MLS constructs, context and IP helpers, network/file policy constructs, conditional expressions, boolif, constrain, call, and optional. Helper tests cover many `CIL_*` node flavors, duplicate handling, merge behavior, null origin, and null extra-argument failures.

## Control Flow
Most tests build a small token tree with `gen_test_tree`, initialize a `cil_db` and `cil_tree_node`, call a `cil_gen_*` builder to populate `test_ast_node->data`, initialize a destination object or symbol table, and call the matching `cil_copy_*` function. Assertions check return code and selected field equality. Node-helper tests first run `cil_build_ast`, then call `__cil_copy_node_helper` with a destination root or parent node and assert both `finished` and status.

## State And Persistence
The tests allocate mutable CIL objects, symbol tables, AST roots, and list nodes in memory only. There is no file persistence. State risk is concentrated in ownership and aliasing: copy helpers duplicate some structures while intentionally preserving string values and symbolic references. Some tests merge into the same DB to exercise duplicate-detection semantics.

## Dependencies And Integration Points
This file is registered by `CilTest.c` in the tree suite. It integrates with CIL parser-test helpers from `CilTest.h`, CIL build functions that turn synthetic parse trees into AST datums, symbol table initialization from libsepol, and internal copy APIs not normally exposed as public application APIs.

## Risks
Several tests only assert `SEPOL_OK` without deeply validating copy independence, allocator ownership, or complete nested graph equality. There are commented-out `test_cil_copy_ast` cases and declarations in the header for copy-data-helper and `netifcon_merge` paths that do not appear implemented here, indicating possible stale coverage intent. The tests also rely on hand-built pointer walks through generated parse trees, which are brittle if parse-tree shape changes.

## Test Signals
Strong signals include coverage of nested lists, anonymous contexts/ranges/IPs, symbol-table duplicate failures, merge-vs-copy behavior, malformed origin and null extra arguments, and representative security policy objects. The suite gives useful regression detection for return-code contracts and basic field preservation across AST copying.
