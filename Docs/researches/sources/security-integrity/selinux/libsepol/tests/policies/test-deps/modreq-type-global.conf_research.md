# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-type-global.conf

## Purpose
This module tests a global required type used as the target of an allow rule.

## Important APIs, Types, And Functions
It requires `type type_req_t` and `class file { read write }`, declares marker `mod_global_t`, creates `test_t`, and grants `test_t type_req_t:file { read write }`.

## Control Flow
The positive dependency base satisfies the type and class requirements, allowing link success. The negative base omits `type_req_t`, so global linking should fail with `-3`.

## State And Persistence Behavior
Successful linking adds `test_t`, marker declaration state, and the file allow rule to the base policydb.

## Dependencies And Integration Points
It is the simplest type dependency case for `do_deps_modreq_global()` and validates global symbol scope checks for `SYM_TYPES`.

## Risks And Edge Cases
The fixture does not test type aliases or attributes; the required symbol must be a concrete base type.

## Test Signals
Link success and enabled `mod_global_t` on the met base; `-3` on the unmet base.
