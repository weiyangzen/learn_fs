# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_fqn.c

## Purpose
This file tests full qualified-name processing for CIL ASTs. It ensures that `cil_fqn_qualify` succeeds on representative policy fragments after they have been converted from synthetic parse trees into CIL AST nodes.

## Important APIs, Types, And Functions
It includes `policydb.h`, `CuTest.h`, `CilTest.h`, `cil_fqn.h`, and `cil_build_ast.h`. The two test entry points are `test_cil_qualify_name` and `test_cil_qualify_name_cil_flavor`. They use `gen_test_tree`, `cil_db_init`, `cil_build_ast`, and `cil_fqn_qualify`.

## Control Flow
Each test builds an in-memory token array, converts it to a parser tree, initializes a CIL database, builds the AST at `test_db->ast->root`, then calls `cil_fqn_qualify`. The first case includes categories, category order, sensitivity, sensitivitycategory, type, role, user, context, and sid references. The second case checks the CIL-flavor class syntax with `inherits`.

## State And Persistence
All state is in memory: parse tree, CIL database, AST, and symbols. There is no teardown visible in the tests, so the unit runner relies on process lifetime for cleanup. The relevant state behavior under test is name qualification over the AST rather than durable storage.

## Dependencies And Integration Points
These tests depend on build-AST success before FQN qualification can run. They are registered in `CilTest.c` and integrate the parser helper, CIL AST builder, and FQN qualification pass. They provide a bridge signal between syntax construction and later semantic resolution.

## Risks
The assertions only check `SEPOL_OK`; they do not inspect the qualified names or verify exact namespace transformations. This can miss regressions where qualification succeeds but produces wrong names. Coverage is narrow, with one larger policy fragment and one class-inheritance flavor case.

## Test Signals
The tests signal that the FQN pass must accept normal CIL policy identifiers, MLS-related names, context references, sid references, and the `class ... inherits ...` flavor without rejecting the AST.
