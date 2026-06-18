# sources/storage-engines/pebble/internal/base/internal_test.go

Purpose: Tests the internal key data model and ordering invariants.

APIs and types: Covers `InternalKey.Encode`, `DecodeInternalKey`, `InternalCompare`, `ParseKind`, key kind string roundtrips, `InternalKey.Separator`, and `IsExclusiveSentinel`.

Control flow and state: The tests encode internal keys into buffers, decode invalid short keys, sort/compare keys with equal and differing user keys, and validate separator results over representative key pairs.

Persistence and dependencies: Verifies the durable trailer encoding and kind names used in debug strings and file formats. Uses the default comparer and testify/datadriven-style assertions.

Integration points: Protects the ordering contract depended on by memtables, SSTable block indexes, merging iterators, and compaction.

Risks: Table coverage is meaningful but not exhaustive across every key kind. Parser helpers intentionally panic on invalid input, so invalid-string behavior is only selectively tested.

Test signals: Strong regression signal for key encoding/order and sentinel semantics.
