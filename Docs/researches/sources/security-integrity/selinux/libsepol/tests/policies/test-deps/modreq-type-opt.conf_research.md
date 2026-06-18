# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-type-opt.conf

## Purpose
This module tests a type required only inside an optional block.

## Important APIs, Types, And Functions
Global scope requires `type file_t` and `class file { read write }`, then declares `mod_global_t`. The optional block requires `type_req_t`, declares `mod_opt_t`, and grants `type_req_t file_t:file { read write }`.

## Control Flow
Both positive and negative bases should link because the missing type is optional. The optional block is enabled only when `type_req_t` is present.

## State And Persistence Behavior
The global declaration persists in both cases; optional allow-rule state is active only for the positive base. Disabled optional state remains inspectable through `mod_opt_t`.

## Dependencies And Integration Points
This fixture targets optional `SYM_TYPES` require handling and its interaction with allow-rule validation.

## Risks And Edge Cases
The allow rule uses a base type as source and another base type as target, so module-local type mapping is not stressed.

## Test Signals
Link return `0` for both bases, with `decl->enabled == 1` only when `type_req_t` exists.
