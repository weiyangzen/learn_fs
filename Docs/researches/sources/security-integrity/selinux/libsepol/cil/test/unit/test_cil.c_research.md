# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil.c

## Purpose
`test_cil.c` contains focused unit tests for core CIL database and symbol-table selection behavior. It validates initialization and `cil_get_symtab()` routing for several AST parent flavors and negative inputs.

## Important APIs, Types, And Functions
The tests call `cil_symtab_array_init()`, `cil_db_init()`, `cil_tree_node_init()`, and `cil_get_symtab()`. Test functions include `test_cil_symtab_array_init()`, `test_cil_db_init()`, `test_cil_get_symtab_block()`, `test_cil_get_symtab_class()`, `test_cil_get_symtab_root()`, `test_cil_get_symtab_flavor_neg()`, `test_cil_get_symtab_null_neg()`, `test_cil_get_symtab_node_null_neg()`, and `test_cil_get_symtab_parent_null_neg()`.

## Control Flow
Each test allocates or initializes a minimal `struct cil_db` and/or `struct cil_tree_node`, configures parent flavor and line fields, calls the target API, and asserts `SEPOL_OK` or `SEPOL_ERR` plus expected pointer state. Positive `cil_get_symtab()` cases cover block, class, and root parent flavors. Negative cases cover invalid flavor, null parent, null node, and parent-null paths.

## State And Persistence
The tests allocate in-memory CIL database and tree-node objects. They do not write files or persistent state. Some tests free manually allocated `struct cil_db` memory, while `test_cil_db_init()` does not clean up the created database before returning.

## Dependencies And Integration Points
The file includes libsepol policydb headers, `CuTest.h`, its own `test_cil.h`, and CIL internal/tree headers. `CilTest.c` registers these functions in `CilTreeGetSuite()`.

## Risks
The tests are useful smoke coverage but not exhaustive. A TODO notes that the `SEPOL_ERR` path in `cil_db_init()` is not reached. Some initialized databases and nodes are not destroyed, which is acceptable for short unit runs but limits leak-check cleanliness. The positive class case requests `CIL_SYM_BLOCKS`, so it validates current routing behavior but may be surprising if symbol routing is refactored.

## Test Signals
Passing tests signal that basic CIL database initialization creates AST/symtab structures and that `cil_get_symtab()` handles common parent flavors and null/error paths consistently.
