# sources/security-integrity/selinux/libsepol/tests/test-deps.c

## Purpose
This CUnit suite verifies libsepol module dependency checking for global and optional `require` blocks across types, attributes, object classes, booleans, roles, and permissions.

## Important APIs, Types, And Functions
Key functions are `deps_test_init()`, `deps_test_cleanup()`, `do_deps_modreq_global()`, `deps_modreq_global()`, `do_deps_modreq_opt()`, `deps_modreq_opt()`, and `deps_add_tests()`. Static arrays `bases_met[NUM_BASES]` and `bases_notmet[NUM_BASES]` hold separate loaded base policydbs.

## Control Flow
Initialization loads many copies of the positive and negative base fixtures. Each test loads a module, suppresses expected error logging through `sepol_handle_t`, calls `link_modules()`, checks the return value, destroys the module, and if appropriate inspects the linked declaration containing a marker type.

## State And Persistence Behavior
Each base policydb is mutated by a single link scenario and kept separate to avoid cross-test contamination. Cleanup destroys all base policydbs.

## Dependencies And Integration Points
The suite depends on `test_load_policy()`, `test_find_decl_by_sym()`, `link_modules()`, sepol handles/message callbacks, and all `test-deps` policy fixtures.

## Risks And Edge Cases
The test uses numeric base indexes that must align with the module matrix. Optional permission behavior intentionally expects a link failure in the negative case, unlike most optional symbol families.

## Test Signals
CUnit tests `deps_modreq_global` and `deps_modreq_opt` validate return values (`0` or `-3`) and declaration enablement for marker types.
