# sources/security-integrity/selinux/libsepol/tests/test-common.h

## Purpose
This header publishes the common policydb assertion helpers used by multiple libsepol test suites.

## Important APIs, Types, And Functions
It includes `<sepol/policydb/policydb.h>` and declares `test_sym_presence()`, `test_policydb_indexes()`, `test_alias_datum()`, `test_role_type_set()`, and `test_attr_types()`.

## Control Flow
There is no runtime control flow in the header. Its comments document expected inputs for each helper and how tests should pass policydbs, symbol names, declarations, expected type arrays, and flags.

## State And Persistence Behavior
The header carries no state. It exposes helpers that inspect `policydb_t`, `avrule_decl_t`, `role_datum_t`, and symbol table state owned elsewhere.

## Dependencies And Integration Points
It is included by expander, linker, and other test files that need consistent policydb structural assertions.

## Risks And Edge Cases
The API exposes internal libsepol data types, so changes to policydb internals can require broad test updates. The comments are part of the contract for correct helper usage.

## Test Signals
Successful compilation of users confirms the expected helper signatures remain stable; runtime signals come from the implementations in `test-common.c`.
