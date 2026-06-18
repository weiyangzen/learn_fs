# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-bool-opt.conf

## Purpose
This optional dependency fixture tests a boolean required only inside an optional block.

## Important APIs, Types, And Functions
The global module requires only `class file { read write }` and declares `mod_global_t`. The optional block requires `bool_req`, declares `a_t`, `b_t`, and marker `mod_opt_t`, then uses `if (bool_req)` around an allow rule.

## Control Flow
The linker should always accept the module. When the base provides `bool_req`, the optional block is enabled and its conditional rule is available. When absent, the optional declaration is disabled.

## State And Persistence Behavior
The test validates conditional policy state inside an optional declaration. Disabled optional state should not activate types or conditional rules, but it must remain findable enough for `test_find_decl_by_sym()` to inspect `mod_opt_t`.

## Dependencies And Integration Points
It integrates boolean dependency resolution, optional declaration enablement, and conditional rule parsing in the module linker.

## Risks And Edge Cases
Because the allow rule is only parsed when the optional block exists, errors can manifest as either dependency handling failures or conditional parse/link failures.

## Test Signals
The return value should be `0` for both bases, with `decl->enabled` toggling according to `bool_req` availability.
