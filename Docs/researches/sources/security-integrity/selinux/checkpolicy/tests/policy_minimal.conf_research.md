# sources/security-integrity/selinux/checkpolicy/tests/policy_minimal.conf

## Purpose

`policy_minimal.conf` is the smallest non-MLS policy fixture in this test subset. It verifies that checkpolicy can round-trip a minimal policy with one class, one SID, one type, one allow rule, one role, one role-type assignment, one user, and one SID context.

## Control Flow And Integration

`test_roundtrip.sh` compiles and decompiles this file with `-E` and with `-E -S -O`, using the same file as both source and expected output. That means no canonical text changes are expected for this minimal policy.

## State And Persistence

The compiled policy persists a single `kernel` SID context `USER1:ROLE1:TYPE1`, a single object class permission, and the minimum type/role/user relationships required for the allow rule and context to be valid.

## Dependencies And Risks

The fixture depends on base checkpolicy grammar and the `-E` option used by the test harness. Because it is intentionally tiny, it is a good smoke test but provides little coverage for ordering, optimizer, aliases, constraints, conditionals, or context normalization.

## Test Signals

The expected signal is exact self-round-trip identity. A diff here indicates a basic parser/decompiler or canonical output regression that should be investigated before interpreting broader fixture failures.
