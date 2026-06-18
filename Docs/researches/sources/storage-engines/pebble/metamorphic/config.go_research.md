# sources/storage-engines/pebble/metamorphic/config.go

## Purpose
`metamorphic/config.go` defines the operation mix and key-format abstraction for Pebble metamorphic tests. It is the central configuration surface controlling which database, iterator, batch, ingest, range-key, and external-object operations are generated and how keys are produced.

## Important APIs, types, and functions
`OpType` enumerates all generated operation kinds. `OpConfig` stores operation weights, new-prefix probability, write suffix distribution, and instance count. Configuration constructors and mutators include `DefaultOpConfig`, `ReadOpConfig`, `WriteOpConfig`, `multiInstanceConfig`, `WithNewPrefixProbability`, and `WithOpWeight`. `KeyFormat` and `KeyGenerator` define the interface for testkeys and Cockroach-style key generation. Registries include `knownKeyFormats` and `keyFormatsByName`.

## Control flow and state behavior
Default config emphasizes iterator and writer operations, with nonzero weights for flushing, restarting, compaction, ingest, range keys, snapshots, and external-file ingestion. Preset configs include a version-heavy workload with low new-prefix probability and reduced deletes. Read-only and write-only configs zero out the other side of the workload. Multi-instance config enables replication while disabling unsupported single deletes, merges, and external ingestion.

`OpConfig` is value-based: mutators return modified copies. The embedded `randvar.Dynamic` suffix distribution is mutable during generation, allowing key generators to expand the suffix range over time.

There is no persistence in this file, but generated operation streams and test options downstream depend on these distributions.

## Dependencies and integration points
The file depends on Pebble operation types, `randvar`, `base.Comparer`, `sstable` block properties, and key formats from testkeys and Cockroach. It is consumed by metamorphic operation generation, command-line/config parsing code, and example tests.

## Risks and test signals
Risks are skewed or invalid operation mixes, stale `NumOpTypes` alignment with the weights array, unsupported operations in special modes, and key-format implementations that do not honor bounds or suffix ordering. Coverage is broad through metamorphic generator/parser/options tests and execution examples, but changes to weights can shift bug-finding power without failing deterministic tests.
