# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-role-opt.conf

## Purpose
This optional dependency module tests role requirements inside an optional declaration.

## Important APIs, Types, And Functions
Global scope requires only `class file { read write }` and declares `mod_global_t`. The optional block requires `role_req_r` and `user_r`, declares `mod_opt_t`, and creates `allow role_req_r user_r`.

## Control Flow
The linker should accept the module against both bases. The optional declaration should be enabled only when the base provides the required roles.

## State And Persistence Behavior
The policydb retains global module state in both paths. Role allow state from the optional block is active only when the declaration is enabled.

## Dependencies And Integration Points
This file exercises optional role scope resolution and role allow rule merging.

## Risks And Edge Cases
Only role existence is tested; role attributes or role type-set expansion are not covered here.

## Test Signals
Both links return `0`; `mod_opt_t` declaration enablement tracks whether `role_req_r` is present.
