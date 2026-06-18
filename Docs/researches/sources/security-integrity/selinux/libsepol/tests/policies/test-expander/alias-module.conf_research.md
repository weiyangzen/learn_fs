# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/alias-module.conf

## Purpose
This small module supplies a type alias needed by the alias expansion tests.

## Important APIs, Types, And Functions
It requires `type alias_check_3_t` and declares `typealias alias_check_3_t alias alias_check_3_a`.

## Control Flow
When linked with `alias-base.conf`, this module makes `alias_check_3_a` available. That in turn satisfies the base optional block requiring the alias and permits a rule involving the alias.

## State And Persistence Behavior
The linked policydb gains a module alias datum whose primary is the base type. Expansion must retain enough alias state for alias datum assertions to distinguish alias versus primary flavor.

## Dependencies And Integration Points
It directly integrates with `test_alias_datum()` and the base optional block in `alias-base.conf`.

## Risks And Edge Cases
If alias requirements are resolved before module aliases are visible to base optionals, the dependent optional block can be incorrectly disabled.

## Test Signals
Expected signals are successful module link and an alias datum for `alias_check_3_a` pointing at `alias_check_3_t`.
