# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_copy_ast.h

## Purpose
This header declares the CuTest entry points for CIL copy-AST tests. It is the suite-facing contract consumed by `CilTest.c` and implemented primarily by `test_cil_copy_ast.c`.

## Important APIs, Types, And Functions
It includes `CuTest.h` and declares `void test_cil_copy_...(CuTest *)` functions for list copying, each major CIL datum copy helper, fill helpers for level/context/IP address, conditional/boolif/constrain copy paths, direct AST copy tests, internal node-helper tests, and copy-data-helper tests.

## Control Flow
The header has no executable control flow. Its declarations allow the test registrar to add copy tests to the CuTest suite. At runtime, registered functions follow the implementation file's pattern of generating a source CIL object, copying it through `cil_copy_*` or `__cil_copy_node_helper`, and asserting return values and selected fields.

## State And Persistence
There is no persistent state. The file influences build state by requiring function signatures to match implementation and suite registration. Mismatches can surface as link failures only when a declared test is actually registered or referenced.

## Dependencies And Integration Points
The only direct dependency is CuTest. The declared functions integrate indirectly with `CilTest.c`, `test_cil_copy_ast.c`, `cil_copy_ast`, `cil_build_ast`, `cil_internal`, and libsepol symbol table behavior.

## Risks
The header declares `test_cil_copy_node_helper_netifcon_merge`, `test_cil_copy_data_helper`, `test_cil_copy_data_helper_getparentsymtab_neg`, and `test_cil_copy_data_helper_duplicatedb_neg`, but the read implementation did not show matching function bodies. It also declares `test_cil_copy_ast` and `test_cil_copy_ast_neg`, whose implementation is commented out and whose registrations are commented in `CilTest.c`. This drift is a maintenance risk and can hide intended coverage.

## Test Signals
The declaration set shows intended coverage across direct copy functions, helper traversal, duplicate negative paths, null argument paths, and nested object fills. It is a useful map of copy-AST coverage expectations even where implementation or registration lags behind the declarations.
