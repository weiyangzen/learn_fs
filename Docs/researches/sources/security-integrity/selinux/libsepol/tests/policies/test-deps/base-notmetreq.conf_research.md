# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/base-notmetreq.conf

## Purpose
This is the negative counterpart to `base-metreq.conf`. It provides a valid base policy that intentionally omits the module-required symbols for dependency failure and disabled-optional tests.

## Important APIs, Types, And Functions
The file retains the broad class, common permission, MLS, type, role, user, boolean, SID, `fs_use_xattr`, and `genfscon` scaffolding needed to parse and link modules. It intentionally lacks `type_req_t`, `attr_req`, `bool_req`, and `role_req_r`; it also omits or changes dependency-relevant object class availability compared with the positive base.

## Control Flow
`deps_test_init()` loads this file into each `bases_notmet[]` slot. Global-require module tests link against it and expect `link_modules()` to fail with `-3`. Optional-require module tests often still expect link success, but the optional declaration containing `mod_opt_t` should be disabled or absent.

## State And Persistence Behavior
The file initializes complete base policy state, but linking should not merge declarations that rely on unmet optional requires. For global unmet requires, linking stops with a dependency error and the module is destroyed without any further assertions on enabled declarations.

## Dependencies And Integration Points
It is paired with all `modreq-*` fixtures and consumed by `do_deps_modreq_global()` and `do_deps_modreq_opt()`. The fixture is also a guard against dependency resolution incorrectly consulting optional base declarations that should not satisfy a module global requirement.

## Risks And Edge Cases
The negative signal depends on absence, so adding a convenient test symbol can silently invalidate an entire dependency lane. Optional permission tests are stricter than most optional tests because missing permissions can still produce `-3` instead of a disabled declaration.

## Test Signals
Global require tests should return `-3`. Optional tests should either link with disabled marker declarations or, for the permission optional case, return the expected failure. Any unexpected `0` for a global missing requirement is a dependency-check regression.
