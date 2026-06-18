# sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/module_add_symbols.conf

## Purpose
This module fixture supplies one symbol of each major family for hook tests that add policy symbols.

## Important APIs, Types, And Functions
It requires `class file { read write }`, declares `type_add_1`, `attribute attrib_add_1`, `role role_add_1`, `bool bool_add_1 false`, and in non-MLS mode declares `user user_add_1 roles { role_add_1 }`.

## Control Flow
The fixture is processed by hooks or linker tests to add symbols and then compare the resulting policydb against an expected policy.

## State And Persistence Behavior
Successful processing mutates symbol tables for types, attributes, roles, booleans, and sometimes users. MLS configuration controls whether user state is added.

## Dependencies And Integration Points
It integrates with policy symbol creation hooks and policydb index validation for added symbols.

## Risks And Edge Cases
The user declaration is under an inverse MLS guard, so test expectations must branch by MLS mode. It does not assign the new type to the new attribute.

## Test Signals
Expected signals are successful addition and correct indexing of the declared symbols, with user addition only in non-MLS mode.
