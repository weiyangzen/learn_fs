# sources/storage-engines/pebble/internal/testkeys/testkeys_test.go

## Purpose
This file validates the `testkeys` package's deterministic keyspace generation, comparer behavior, suffix handling, random prefix generation, and KV metadata parsing.

## Important APIs, Types, and Functions
Tests include `TestGenerateAlphabetKey`, `TestKeyCount`, `TestFullKeyspaces`, `TestSlice`, `TestSuffix`, `TestSuffixLen`, `TestDivvy`, `TestRandomPrefixInRange`, `TestOverflowPanic`, `TestComparer`, `TestIgnorableSuffix`, and `TestExtractKVMeta`. `keyspaceToString` formats keyspaces for comparisons.

## Control Flow and State
Most tests are table-driven. `TestDivvy` uses datadriven fixtures. `TestRandomPrefixInRange` performs both fixed scenario sampling and a randomized insertion process that keeps a sorted key list and verifies each generated prefix fits between selected bounds. `TestOverflowPanic` intentionally recovers from a panic.

## Dependencies and Integration
The file depends on `datadriven`, Pebble `base`, `testify/require`, and `math/rand/v2`. It anchors test-key semantics used throughout many Pebble tests.

## Risks and Gaps
Randomized prefix generation is deterministic due to fixed PCG seed, but it is still sample-based. The tests do not cover every invalid key validation path or every comparer callback under all suffix/prefix combinations.

## Test Signals
The comparer is checked through `base.CheckComparer`, giving high confidence that testkeys obey Pebble comparer invariants. The `_synthetic` tests explicitly document point-vs-range suffix divergence.
