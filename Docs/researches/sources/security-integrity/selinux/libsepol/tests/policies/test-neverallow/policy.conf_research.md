# sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy.conf

## Purpose
This policy fixture tests libsepol neverallow and neverallowxperm assertion checking across ordinary allows, attributes, complements, wildcards, self, audit/dontaudit, transitions, and extended permissions.

## Important APIs, Types, And Functions
It declares minimal classes `process` and `file` plus permissions including `ioctl`, many test types and attributes (`test1_t` through `test26_*`), `allow`, `auditallow`, `dontaudit`, `type_transition`, `neverallow`, `allowxperm`, and `neverallowxperm` rules. Comments marked `nofail` identify rules expected not to violate assertions.

## Control Flow
The policy is loaded by neverallow tests, then libsepol assertion evaluation compares each allow or extended-permission allow against neverallow constraints. The numbered blocks isolate one semantic case at a time.

## State And Persistence Behavior
The policydb records assertion rules and allowed access-vector/extended-permission rules. It also carries the minimal users, SIDs, MLS data, and fs_use declarations required for a valid binary policy.

## Dependencies And Integration Points
It integrates with assertion checking logic for type sets, attributes, complements, wildcard permissions, `self`, non-allow rules, and ioctl extended permission ranges.

## Risks And Edge Cases
Many blocks are intentionally violating. A test harness must know expected failure counts or failure locations; otherwise a successful compile can still mean assertions were not checked.

## Test Signals
Signals include detection of expected neverallow violations, non-detection for `nofail` blocks, and correct handling of xperm singleton and range intersections.
