# sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy_not_self.conf

## Purpose
This companion fixture tests neverallow target expressions using `~self`.

## Important APIs, Types, And Functions
It mirrors many cases from `policy_minus_self.conf`, but uses targets such as `~self` or `~{ self test6_1_t }`. It includes custom classes, attributes, ordinary allows, xperm allows, and neverallowxperm ranges through test 31.

## Control Flow
Each block checks whether a non-self complement target intersects the corresponding allow relation. Extended-permission blocks test the same target semantics with ioctl singleton and range permissions.

## State And Persistence Behavior
The policydb must represent `~self` as a relation-dependent complement rather than a single static type set. Attribute expansion and xperm range storage are both involved.

## Dependencies And Integration Points
It integrates with neverallow type-set complement logic, self relation evaluation, attribute expansion, and xperm assertion checking.

## Risks And Edge Cases
`~self` and `{ set -self }` look similar but differ in universe and exclusion behavior. Reusing code paths without preserving those semantics can produce false positives or false negatives.

## Test Signals
Signals are correct assertion outcomes for non-self conflicts and non-conflicts, especially in the later attribute/xperm violation cases.
