# sources/storage-engines/pebble/internal/base/doc.go

Purpose: Package documentation for `internal/base`, describing Pebble's internal key/value model, LSM layout, levels, memtables, log-structured writes, compaction, range tombstones, snapshots, and comparer semantics.

APIs and types: Exposes no runtime API beyond the `package base` declaration. The file is a long package comment, so its API value is conceptual rather than executable.

Control flow and state: Documents how writes enter WAL and memtable, flushes create L0 tables, compactions merge and rewrite levels, snapshots constrain obsolete-key collection, and range tombstones delete half-open spans.

Persistence and dependencies: Describes durable structures used across the package: WALs, manifests, SSTables, internal key trailers, sequence numbers, and comparer ordering.

Integration points: Sets expectations for downstream packages that use `base.InternalKey`, comparers, file numbers, iterator contracts, and compaction invariants.

Risks: Documentation must remain synchronized with evolving key kinds and LSM behavior. Drift here is risky because it describes rules that many lower-level packages assume.

Test signals: No direct tests; correctness is indirectly enforced by tests for internal keys, filenames, iterators, compactions, and table behavior.
