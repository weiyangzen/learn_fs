# sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/small-base.conf

## Purpose
This is the small base policy used by hook tests before programmatic symbol or rule additions.

## Important APIs, Types, And Functions
It declares the ordinary class and MLS scaffolding plus `g_b_type_1`, roles `g_b_role_1`, `g_b_role_2`, `g_b_role_3`, `g_b_type_2`, and a disabled optional block requiring `invalid_type` that would add role allow and transition rules.

## Control Flow
Hook tests start from this base, apply additions from hook modules or direct APIs, and compare the resulting state to `cmp_policy.conf`.

## State And Persistence Behavior
The base policydb holds active core symbols and disabled optional state. It also includes user and context state for `g_b_user_1` and filesystem context declarations.

## Dependencies And Integration Points
It is the input side of hook comparison tests and integrates with policydb mutation APIs.

## Risks And Edge Cases
The file is nearly identical to `cmp_policy.conf`; any intentional difference must align with the hook operation under test. Disabled optional leakage is a key risk.

## Test Signals
Expected signals are successful base loading and deterministic policydb comparison after hooks run.
