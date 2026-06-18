# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-attr-opt.conf

## Purpose
This module tests attribute requirements inside an optional block. The outer module should link even when `attr_req` is missing, while the optional declaration should be disabled.

## Important APIs, Types, And Functions
The global `require` only asks for `class file { read write }`; the global marker is `mod_global_t`. The optional block requires `attribute attr_req`, declares marker `mod_opt_t`, and assigns `new_t` to `attr_req`.

## Control Flow
`do_deps_modreq_opt()` loads the module and expects link success for both positive and negative bases. It locates `mod_opt_t` and checks `decl->enabled`: `1` when `attr_req` exists and `0` when it does not.

## State And Persistence Behavior
The global declaration always exists. The optional declaration is conditionally merged into active policy state based on requirement satisfaction, preserving disabled declaration metadata for inspection.

## Dependencies And Integration Points
This file exercises the linker’s optional-block dependency resolver and its ability to keep global module scope independent from optional scope.

## Risks And Edge Cases
If disabled declarations are dropped instead of retained, the test lookup by `mod_opt_t` can fail differently from an enabled-state mismatch. The file has no allow rule using the attribute, so it mainly tests symbol presence and membership parsing.

## Test Signals
Expected signals are link return `0` in both cases and enabled-state matching the base’s attribute availability.
