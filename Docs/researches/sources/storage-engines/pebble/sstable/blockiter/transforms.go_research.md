## sources/storage-engines/pebble/sstable/blockiter/transforms.go

Purpose: Defines logical transforms applied during block iteration, including synthetic sequence numbers, hiding obsolete points, synthetic prefixes, and synthetic suffixes.

Important APIs/types/functions: `Transforms`, `NoTransforms`, `FragmentTransforms`, `NoFragmentTransforms`, `SyntheticSeqNum`, `NoSyntheticSeqNum`, `SyntheticSuffix`, `SyntheticPrefix`, `SyntheticPrefixAndSuffix`, `MakeSyntheticPrefixAndSuffix`, accessors, `SyntheticPrefix.Apply`, `SyntheticPrefix.Invert`, and `SyntheticPrefixAndSuffix.RemoveSuffix`.

Control flow: `NoTransforms` checks all transform flags. Prefix/suffix helpers expose compact slices backed by one allocated buffer stored through an unsafe pointer. `MakeSyntheticPrefixAndSuffix` returns a zero value when both inputs are empty; otherwise it copies prefix then suffix into one buffer. `RemoveSuffix` preserves the prefix backing pointer and zeroes suffix length.

State and persistence behavior: These transforms are runtime iterator behavior, often for external/foreign/virtual tables, and do not rewrite physical blocks. Synthetic sequence numbers override key trailers when surfacing keys. Synthetic prefix/suffix changes logical keys seen by readers while underlying table bloom filters and comparisons may still operate on physical partial keys under documented constraints.

Dependencies and integration points: Used by row/column block iterators, fragment/range-key iterators, block-property synthetic suffix filtering, and external ingestion/virtual table code. Depends on `base`, `bytes`, `unsafe`, and `errors`.

Risks: Unsafe pointer backing relies on the allocated slice escaping and remaining live through the struct. Synthetic suffix has strict correctness constraints: unique prefixes, replacement suffix ordering, no range deletions, limited range-key support. `SyntheticPrefix.Invert` panics if called with a non-matching key.

Test signals: `transforms_test.go` covers zero/nonzero transform detection, prefix/suffix accessors, and `RemoveSuffix`.
