# sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy_cond.conf

## Purpose
This fixture tests neverallow and neverallowxperm interactions with conditional policy rules.

## Important APIs, Types, And Functions
It declares booleans `boolean1` and `boolean2`, minimal classes and MLS state, test types `test1_t` through `test15_t`, conditional `allow` and `allowxperm` rules, and corresponding `neverallow`/`neverallowxperm` assertions. It ends with SID contexts and fs_use declarations.

## Control Flow
Each numbered test places allows behind boolean expressions and checks whether assertion logic considers possible conditional states. Some cases are marked `nofail` where the conditional expression or xperm set should not intersect the assertion.

## State And Persistence Behavior
The policydb stores conditional nodes with true/false rule lists plus assertion rules. Boolean default values seed initial state but assertion checking must reason about conditional policy, not just defaults.

## Dependencies And Integration Points
It integrates with conditional expression parsing, conditional AV rule storage, and neverallowxperm set-intersection logic.

## Risks And Edge Cases
Conditional neverallow behavior is easy to under-check if only the default boolean branch is examined. Xperm conditions add another dimension of range/singleton intersection risk.

## Test Signals
Expected signals are assertion failures for conditionally reachable conflicts and no failures for explicitly non-overlapping or `nofail` conditional cases.
