## sources/storage-engines/pebble/sstable/blockiter/transforms_test.go

Purpose: Unit-tests transform zero-value behavior and compact synthetic prefix/suffix storage.

Important APIs/types/functions: `TestTransforms`, `TestFragmentTransforms`, and `TestSyntheticPrefixAndSuffix`.

Control flow: The first two tests verify that zero transforms and explicitly empty prefix/suffix pairs count as no transforms, while `HideObsoletePoints`, nonzero synthetic sequence numbers, nonempty prefix, and nonempty suffix make transforms active. The prefix/suffix test constructs prefix+suffix, prefix-only, suffix-only, and removed-suffix cases, asserting accessors and lengths.

State and persistence behavior: Tests runtime transform value semantics, not persisted SSTable data.

Dependencies and integration points: Uses `stretchr/testify/require` and the `blockiter` package.

Risks: Does not test `SyntheticPrefix.Apply`/`Invert` or GC/lifetime behavior of the unsafe backing pointer. Does not test semantic restrictions around suffix ordering.

Test signals: Good signal for the public value-type API and default no-transform contracts.
