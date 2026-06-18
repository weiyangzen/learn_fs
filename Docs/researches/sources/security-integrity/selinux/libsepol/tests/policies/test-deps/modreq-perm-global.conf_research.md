# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-perm-global.conf

## Purpose
This module tests global permission requirements for an existing object class.

## Important APIs, Types, And Functions
It requires `class msg { send receive }`, declares marker `mod_global_t`, creates `a_t` and `b_t`, and grants `msg` `send` and `receive`.

## Control Flow
The dependency suite links this fixture against base policies where the `msg` class and permissions are either present or not sufficient. Positive linking enables the marker declaration; negative linking should return `-3`.

## State And Persistence Behavior
On success, the base gains module types and an access-vector rule tied to the `msg` class. The fixture does not persist external state beyond the mutated in-memory policydb.

## Dependencies And Integration Points
It specifically exercises permission-level require checking rather than only object-class presence.

## Risks And Edge Cases
A test base with `msg` but a partial permission set could expose more subtle failures than the current positive/negative split. This fixture assumes exact permission availability.

## Test Signals
Expected signals are positive link success, negative link failure, and enabled `mod_global_t` in the positive base.
