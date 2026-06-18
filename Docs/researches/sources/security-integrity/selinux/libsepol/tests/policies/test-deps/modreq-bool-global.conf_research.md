# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-bool-global.conf

## Purpose
This module fixture tests a global required boolean used in a conditional rule.

## Important APIs, Types, And Functions
It requires `bool bool_req` and `class file { read write }`, declares marker `mod_global_t`, creates `a_t` and `b_t`, and gates an `allow a_t b_t:file { read write }` rule behind `if (bool_req)`.

## Control Flow
The dependency test links this module against both base variants. A positive link validates that required booleans can be referenced in module conditional expressions; a negative link should fail before conditional rules are active.

## State And Persistence Behavior
On success, the linked base gains a conditional node referencing a base boolean and a module allow rule. On failure, no lasting state should be assumed after the module is destroyed.

## Dependencies And Integration Points
The module integrates global dependency checking with conditional expression parsing and the conditional rule list generated from the `if` block.

## Risks And Edge Cases
The boolean is only tested as a simple positive identifier. There is no nested expression, negation, or optional boolean reference in this fixture.

## Test Signals
Expected signals are link success only with `bool_req` present and an enabled declaration for `mod_global_t` in the positive case.
