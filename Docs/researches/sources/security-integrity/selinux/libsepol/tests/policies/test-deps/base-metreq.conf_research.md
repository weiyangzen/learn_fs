# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/base-metreq.conf

## Purpose
This base policy fixture is the positive dependency baseline for `test-deps.c`. It declares the normal class, MLS, role, user, type, boolean, and context scaffolding plus the exact symbols that module require tests expect to be present.

## Important APIs, Types, And Functions
Key dependency symbols are `type_req_t`, `attr_req`, `bool_req`, and `role_req_r`. It also includes object classes including `sem` and `msg` with the permissions tested by module fixtures, ordinary types such as `system_t`, `sysadm_t`, `file_t`, and `fs_t`, attributes such as `domain` and `files`, and booleans such as `secure_mode`.

## Control Flow
`deps_test_init()` loads this file into each `bases_met[]` slot. Global-require tests link one module into a copy and expect `link_modules()` to return success. Optional-require tests use it to enable optional module declarations when the required symbol exists.

## State And Persistence Behavior
The fixture builds a reusable base `policydb_t` per dependency case. Linking mutates each base by merging module declarations and enabling optional blocks whose requirements are satisfied. The file also seeds SID, fs_use, genfscon, and user context state needed for a complete policydb.

## Dependencies And Integration Points
It integrates with every `modreq-*-global.conf` and `modreq-*-opt.conf` fixture. `test_find_decl_by_sym()` later locates module marker types such as `mod_global_t` or `mod_opt_t` in the linked base to verify declaration enablement.

## Risks And Edge Cases
If this fixture accidentally diverges from `base-notmetreq.conf` in unrelated class or MLS scaffolding, dependency failures may be misattributed. The positive symbols must remain minimal and intentional, especially `sem`, `msg`, and the required role/type/attribute/boolean names.

## Test Signals
Expected signals are zero return from `link_modules()` for positive cases and enabled declarations for marker symbols. A missing required symbol should flip a positive case into the same `-3` failure path used by the negative base.
