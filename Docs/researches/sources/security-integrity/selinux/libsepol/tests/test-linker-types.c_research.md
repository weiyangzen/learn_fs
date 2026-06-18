<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-types.c -->
# sources/security-integrity/selinux/libsepol/tests/test-linker-types.c

## Purpose

Exercises libsepol linker handling of types, attributes, aliases, declaration scopes, optional blocks, and type-attribute bitmap placement across base and module policy declarations. The source was read completely for this report (337 lines).

## Important APIs, Types, and Functions

`test_type_datum()` verifies global and declaration-local `type_datum_t` flavor, primary bit, and value consistency. `base_type_tests()` checks base/global/optional symbols and aliases. `module_type_tests()` checks copied module types, merged attributes, optional declaration-local type sets, multi-module additions, and alias mapping.

## Control Flow

The tests locate declarations by tag symbols, assert symbol presence in expected declaration IDs, then validate either type datums, attribute member type sets, or alias datums through local helpers.

## State and Persistence Behavior

No persistent state is owned; all reads are against the `policydb_t *base` supplied by the linker harness.

## Dependencies and Integration Points

Depends on libsepol `policydb` and `link` internals, CUnit, and local helpers such as `test_find_decl_by_sym`, `test_sym_presence`, `test_attr_types`, and `test_alias_datum`.

## Risks and Edge Cases

The risks under test are scope smashing, incorrect optional/global merge behavior, alias primary-value drift, and attribute bitmap updates landing in the wrong declaration table.

## Test Signals

A passing suite is a high-value signal for module linker symbol table correctness for type-related policy constructs.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-types.c -->
