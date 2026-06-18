# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-attr-global.conf

## Purpose
This module fixture tests a global-scope `require` for an attribute. It should link only when the base provides `attr_req`.

## Important APIs, Types, And Functions
The module declares `module modreq_attr_global 1.0`, requires `attribute attr_req`, creates marker type `mod_global_t`, and declares `new_t` as a member of `attr_req`.

## Control Flow
`do_deps_modreq_global()` loads the module, links it into either the positive or negative base, and then searches the linked base for `mod_global_t`. If requirements are met, the declaration containing this marker must be enabled.

## State And Persistence Behavior
When linked successfully, the base policydb gains a module declaration and attribute membership for `new_t`. When the requirement is absent, linking fails before the marker declaration is asserted.

## Dependencies And Integration Points
The module depends directly on `base-metreq.conf` declaring `attr_req`. It integrates with libsepol scope checking for global module requires and type-to-attribute mapping.

## Risks And Edge Cases
The fixture only verifies a single required attribute and one type membership. It does not test inherited attributes, aliases, or multiple required attributes.

## Test Signals
Success with `base-metreq.conf`, `-3` with `base-notmetreq.conf`, and `decl->enabled == 1` for `mod_global_t` are the expected signals.
