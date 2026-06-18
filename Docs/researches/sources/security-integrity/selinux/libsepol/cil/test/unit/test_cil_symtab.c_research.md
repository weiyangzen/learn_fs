# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_symtab.c

Purpose: Implements a focused CuTest for inserting a block datum into a CIL symbol table.

Important APIs and functions: `test_cil_symtab_insert()` calls `cil_tree_node_init`, `cil_db_init`, `cil_symtab_array_init`, `cil_get_symtab`, and `cil_symtab_insert`. It asserts `SEPOL_OK`.

Control flow: The test allocates a `cil_block`, creates a test AST node and database, attaches the node under the database root, initializes the block symbol table array, fetches the root block symbol table, and inserts the block under key `"test"`.

State and persistence: State is in heap-allocated CIL objects and the db root symbol table. The test does not persist policy data and does not explicitly free all allocations, which is acceptable only for short-lived test processes.

Dependencies and integration points: Includes public `sepol/policydb/policydb.h`, CuTest, and internal `cil_tree.h`, `cil_symtab.h`, and `cil_internal.h`.

Risks: The test validates only the success path, not duplicate insertion, invalid keys, cleanup, or null inputs. Manual heap allocation without full cleanup can obscure leak checks.

Test signals: Passing assertion on `SEPOL_OK` and no crash during CIL db/tree setup indicate the symtab insertion path remains usable.
