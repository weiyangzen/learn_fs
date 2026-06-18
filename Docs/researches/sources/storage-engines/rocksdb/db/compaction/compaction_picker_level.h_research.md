# sources/storage-engines/rocksdb/db/compaction/compaction_picker_level.h

## Purpose
Declares `LevelCompactionPicker`, RocksDB's `CompactionPicker` subclass for leveled compaction. The header defines the public picker surface used by column-family setup and compaction scheduling while keeping the detailed selection algorithm in `compaction_picker_level.cc`.

## Important APIs And Types
- `LevelCompactionPicker`: derives from `CompactionPicker` and specializes it for leveled compaction.
- Constructor `LevelCompactionPicker(const ImmutableOptions& ioptions, const InternalKeyComparator* icmp)`: forwards immutable options and the internal-key comparator to the base picker.
- `Compaction* PickCompaction(...) override`: main scheduling entry point. It accepts column-family name, mutable CF/DB options, snapshots/checker placeholders, `VersionStorageInfo`, a `LogBuffer`, `full_history_ts_low`, and an optional `require_max_output_level` flag. The implementation currently ignores snapshot parameters and the flag.
- `bool NeedsCompaction(const VersionStorageInfo*) const override`: readiness probe used by scheduling code to decide whether leveled compaction has pending work.

## Control Flow And State
The header has no executable control flow beyond inline constructor forwarding. Its declarations route all behavior to the `.cc` implementation: `NeedsCompaction()` checks version-storage maintenance queues and compaction scores, while `PickCompaction()` builds exactly one `Compaction` plan or returns null.

The type itself owns no new fields beyond the inherited `CompactionPicker` state. State such as running compactions, input expansion, selected files, compaction scores, and next compaction indexes lives in the base picker, `VersionStorageInfo`, and the local builder in the implementation file.

## Dependencies And Integration Points
- Includes `db/compaction/compaction_picker.h`, which supplies the base class, `Compaction`, option types, `VersionStorageInfo`, `SnapshotChecker`, and comparator-related declarations needed by the method signatures.
- Lives in `ROCKSDB_NAMESPACE`, matching the rest of RocksDB internals.
- Integrated by column-family code that chooses a leveled picker when a column family uses leveled compaction. Downstream compaction scheduling calls `NeedsCompaction()` and `PickCompaction()` polymorphically through `CompactionPicker`.
- The comment links the class to the leveled-compaction design described in RocksDB documentation, but the source contract is the base-class override interface.

## Persistence Behavior
The header itself has no persistence behavior. Because `LevelCompactionPicker` does not declare additional fields, any persistence side effects are indirect and happen in the implementation after a `Compaction` is registered and later executed by the compaction/version-set machinery. The constructor only stores inherited references/options through the base class.

## Risks And Test Signals
The main header-level risk is interface drift: if `CompactionPicker::PickCompaction()` changes, this override must stay signature-compatible or leveled compaction will fail to compile. The optional `require_max_output_level` argument is present for the base interface but ignored by the implementation, so callers should not assume this picker honors it.

Test signals are mostly compile-time and polymorphic runtime coverage: `db/column_family.cc` instantiates this class for leveled compaction, while `db/compaction/compaction_picker_test.cc` and `db/db_compaction_test.cc` exercise the concrete picker through this header's public methods.
