# sources/storage-engines/pebble/sstable/tablefilters/bloom/adaptive_policy_test.go

## Purpose
Validates adaptive Bloom size calculations, capped filter construction, empty/too-small behavior, and policy-name parsing.

## Important APIs, Types, And Functions
Tests include `TestFilterSize`, `TestMaxBitsPerKey`, `TestAdaptivePolicy`, and `TestAdaptivePolicyFromName`. Local helpers build filters with deterministic little-endian keys, require size constraints, and check inserted-key membership plus rough FPR sanity.

## Control Flow
`TestFilterSize` compares formula output to actual writer output over randomized counts and bits/key. `TestMaxBitsPerKey` verifies boundary behavior around exact filter sizes and random max sizes. `TestAdaptivePolicy` builds capped filters under full, oversized, half, quarter, empty, too-small, and randomized cases. Name parsing asserts adaptive and non-adaptive cases.

## State And Persistence Behavior
All state is in-memory filter bytes. It verifies serialized byte sizes but does not write SSTables.

## Dependencies And Integration Points
Depends on Bloom policy internals, `base.TableFilterFamily`, and `testify/require`. It protects the adaptive policy used through `tablefilters.PolicyFromName`.

## Risks And Edge Cases
FPR sanity only ensures the filter is not effectively all-true. Randomized tests may not cover every odd-line transition, but exact boundary checks around `FilterSize` cover important math.

## Test Signals
Signals are size equality/inequality, successful membership for inserted keys, rejection of empty or impractically small filters, and correct parsed policy fields.
