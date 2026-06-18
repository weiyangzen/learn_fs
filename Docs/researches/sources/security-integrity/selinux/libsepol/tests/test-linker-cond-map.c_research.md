<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-cond-map.c -->
# sources/security-integrity/selinux/libsepol/tests/test-linker-cond-map.c

## Purpose

Tests that conditional boolean symbols, default states, and conditional expression nodes are preserved and remapped correctly by the module linker. The source was read completely for this report (163 lines).

## Important APIs, Types, and Functions

Defines `test_cond_expr_t`, `test_cond_expr_mapping()`, `test_bool_state()`, `base_cond_tests()`, and `module_cond_tests()`. The checks compare `cond_expr_t` node types and boolean name mapping through `sym_val_to_name[SYM_BOOLS]`.

## Control Flow

For each declaration tag, the test verifies boolean symbol scope, expected boolean state, and the exact postfix expression sequence used by the declaration conditional list.

## State and Persistence Behavior

The file owns no persistent data; it inspects linked policydb structures supplied by the harness.

## Dependencies and Integration Points

Depends on libsepol conditional policydb structures, CUnit, and local linker test helpers.

## Risks and Edge Cases

Risks under test include boolean value remapping errors, default state loss, malformed conditional expression lists, and optional declaration conditional leakage.

## Test Signals

Passing tests indicate boolean and conditional AST remapping survived linker symbol renumbering.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-cond-map.c -->
