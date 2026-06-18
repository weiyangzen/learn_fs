# sources/storage-engines/pebble/metamorphic/cockroachkvs.go

## Purpose
`metamorphic/cockroachkvs.go` defines a metamorphic `KeyFormat` and key generator that mimic CockroachDB MVCC keys. It lets Pebble metamorphic tests exercise comparer behavior, suffix ordering, block-property filters, and timestamp-skewed version histories representative of CockroachDB.

## Important APIs, types, and functions
`CockroachKeyFormat` supplies comparer, key schema, format/parse functions, block property collectors, suffix filters, and generator construction. `cockroachKeyGenerator` implements `KeyGenerator` with `RecordPrecedingKey`, `ExtendPrefix`, `RandKey`, `RandKeyInRange`, `RandPrefix`, `SkewedSuffix`, `IncMaxSuffix`, `SuffixRange`, and `UniformSuffix`. `cockroachSuffixKeyspace` maps one-dimensional `suffixIndex` values to `(wallTime, logical)` MVCC timestamp suffixes.

## Control flow and state behavior
The generator chooses between known keys, existing prefixes with new suffixes, and entirely new prefixes according to `OpConfig`. It uses `keyManager` to avoid or record duplicates and `writeSuffixDist` to skew writes toward recent suffixes. Bounded key generation splits Cockroach keys into prefix and suffix indexes, then generates either an in-range suffix under the same prefix or a random prefix between bounds.

`RecordPrecedingKey` ratchets the suffix distribution upward when prior test state contains larger timestamps, preserving cross-version workload continuity. `SuffixRange` accounts for Cockroach's descending MVCC suffix ordering by returning `(low, high]` in comparer terms.

State is held in the key manager, RNG, op config's mutable suffix distribution, and suffix keyspace mapping. No files are persisted by this source.

## Dependencies and integration points
The file depends on `cockroachkvs`, `testkeys.RandomPrefixInRange`, Pebble key schemas and block-property filters, and metamorphic `keyManager`. It is selected through the key-format registry in `config.go`.

## Risks and test signals
The riskiest areas are suffix ordering, bounded generation under descending timestamp semantics, distribution ratcheting, and consistency between formatted strings and parsed keys. Test signals are indirect through generator/key-manager tests and Cockroach-key metamorphic runs; any comparer or suffix-filter mismatch can produce hard-to-debug nondeterministic failures.
