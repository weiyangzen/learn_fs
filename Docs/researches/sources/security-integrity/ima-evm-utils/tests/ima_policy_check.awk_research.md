
# sources/security-integrity/ima-evm-utils/tests/ima_policy_check.awk

## Purpose
`ima_policy_check.awk` checks whether a proposed IMA policy rule is invalid, overlaps with the currently loaded policy, or already exists. It is used by tests before loading new policy rules to avoid interference.

## Important APIs, Types, And Functions
The script encodes known action keys, policy keyword keys, and option keys. It returns a bitmask: `1` invalid new rule, `2` overlapping rule, and `4` same rule exists. It normalizes `FILE_MMAP` to `MMAP_CHECK` and `PATH_CHECK` to `FILE_CHECK`.

## Control Flow
The first nonempty input line is treated as the new rule; subsequent lines are existing rules. Each rule is parsed into key/value/operator arrays. Invalid keys or non-action first tokens cause immediate invalid-rule exit. Existing rules are compared by action compatibility, shared keywords, value/operator equality, unsupported interval operators, and `^` modifiers.

## State And Persistence
All state is in AWK arrays during one invocation. No files are modified.

## Dependencies And Integration Points
`functions_kernel.sh` pipes the new rule plus `/sys/kernel/security/ima/policy` into this script before signing and loading a temporary policy file.

## Risks
The script intentionally does not understand `<`/`>` interval disjointness and treats `^` modifiers as potentially overlapping. It also cannot prove non-overlap based only on different `func` values because one operation can trigger multiple IMA hooks. These conservative choices can skip or warn on safe combinations.

## Test Signals
`ima_policy_check.test` should cover invalid, overlapping, and duplicate-rule detection. Kernel tests rely on this script to prevent cross-test policy contamination.
