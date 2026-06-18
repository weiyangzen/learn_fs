# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/user-base.conf

## Purpose
This base fixture tests user mapping and expansion, especially MLS-gated user requirements.

## Important APIs, Types, And Functions
Focused symbols are `user_check_1`, roles `user_check_1_1_r` and `user_check_1_2_r`, types `user_check_1_1_t` and `user_check_1_2_t`, and the `gen_user(user_check_1, ...)` declaration. It also contains standard class, MLS, role, type, boolean, SID, and filesystem context scaffolding.

## Control Flow
When MLS is enabled, `user-module.conf` requires `user_check_1`. The base provides that user and its roles, allowing module link and expansion to exercise user symbol visibility.

## State And Persistence Behavior
The parsed policydb contains user datum state, role sets, MLS range, and contexts. Expansion must preserve the user mapping and role associations.

## Dependencies And Integration Points
It integrates with `user-module.conf`, the parser’s `gen_user` macro handling, and user symbol indexing in `policydb_t`.

## Risks And Edge Cases
The module’s user requirement is under `enable_mls`, so MLS/non-MLS runs can cover different dependency paths. User-role range semantics are not deeply asserted by the tiny module.

## Test Signals
Expected signals are successful user symbol resolution in MLS mode and stable user-to-role mapping after expansion.
