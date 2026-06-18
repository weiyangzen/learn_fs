# sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy_minus_self.conf

## Purpose
This fixture focuses on neverallow target sets expressed as `{ set -self }`.

## Important APIs, Types, And Functions
It declares file and custom classes, many numbered test types and attributes, ordinary `allow`, `allowxperm`, `neverallow`, and `neverallowxperm` rules. The central syntax is target sets such as `{ test3_2_t -self }` and attribute sets such as `{ test13_2_a -self }`.

## Control Flow
Numbered tests compare concrete and attribute-sourced allow pairs with neverallow target sets that remove self-pairs. Later tests extend the same pattern to ioctl xperm ranges.

## State And Persistence Behavior
The policydb stores expanded type sets and assertion rules where `self` exclusion must be resolved per source type. Correct behavior depends on evaluating `self` after source/target expansion, not as a static type.

## Dependencies And Integration Points
It integrates with type-set complement/subtraction code, attribute expansion, self semantics, and extended-permission assertion checking.

## Risks And Edge Cases
The semantics of `{ attribute -self }` can differ from `~self`; this fixture protects against collapsing both forms too early. Some duplicated or similarly named attributes make test maintenance error-prone.

## Test Signals
Expected signals are violations only when the non-self target set intersects an allow, and no failures for comments marked `nofail`.
