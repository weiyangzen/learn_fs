# sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/cmp_policy.conf

## Purpose
This comparison policy is the expected baseline for hook tests that add symbols or role rules programmatically.

## Important APIs, Types, And Functions
It declares a small base with `g_b_type_1`, roles `g_b_role_1`, `g_b_role_2`, `g_b_role_3`, type `g_b_type_2`, and an optional block requiring `invalid_type` that would add role allow and role transition rules if enabled.

## Control Flow
Hook tests can load or synthesize a policy, apply modifications, and compare against this known policy shape. The optional block is deliberately disabled because `invalid_type` is absent.

## State And Persistence Behavior
The policydb holds base symbols, user/context state, and disabled optional declaration state. It should not include active rules from the invalid optional.

## Dependencies And Integration Points
It integrates with test hooks that compare policydb contents after adding symbols or role allow/transition rules.

## Risks And Edge Cases
If a hook accidentally enables disabled optional declarations or copies disabled rules into active state, this comparison policy should reveal the mismatch.

## Test Signals
Matching policydb state against this fixture validates that hook-added state has the expected symbols and no unintended optional activation.
