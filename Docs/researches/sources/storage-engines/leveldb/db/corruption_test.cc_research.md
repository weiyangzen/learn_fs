# sources/storage-engines/leveldb/db/corruption_test.cc

## Purpose
This gtest suite validates LevelDB behavior when logs, table files, descriptors, and compaction inputs are corrupted or missing. It checks both tolerant recovery and paranoid error propagation.

## Important APIs, Types, And Functions
`CorruptionTest` owns a `test::ErrorEnv`, tiny block cache, `Options`, and `DB*`. Helpers `Build`, `Check`, `Corrupt`, `RepairDB`, `TryReopen`, `Property`, `Key`, and `Value` create deterministic data, corrupt newest files of a requested `FileType`, and count surviving records. Tests cover recovery, write errors, table corruption, repair, index/footer corruption, descriptor loss/corruption, sequence recovery, compaction input errors, paranoid mode, and unrelated-key writes.

## Control Flow
Most tests populate the DB, force memtable/table compactions via `DBImpl` test hooks, mutate on-disk bytes using the underlying env, reopen or repair, then iterate to count valid keys. Log corruption drops complete corrupted records. Table corruption causes partial data loss or read errors depending on paranoid checks. Descriptor corruption prevents open until repair.

## State And Persistence Behavior
The suite intentionally damages persistent log, table, and manifest/descriptor files. Repair reconstructs metadata from tables and logs and must recover the last sequence number so later writes are not hidden by older entries. `Corrupt` picks the highest-numbered file of a type and flips bytes at absolute or end-relative offsets.

## Dependencies And Integration Points
It integrates `DBImpl`, file naming, WAL format, `VersionSet`, table cache, repair, write batches, `test::ErrorEnv`, block cache, and table checksums. It exercises recovery decisions that normal DB tests do not cover.

## Risks And Edge Cases
The expected key-count ranges tolerate partial loss, so they catch broad safety properties more than exact recovery contents. Corruption offsets assume current file layout. Non-paranoid recovery ignores some errors by design, while paranoid mode should convert corruption into persistent write/open failure.

## Test Signals
Strong signals are bounded surviving record counts, reopen failure on missing/corrupt descriptors under paranoid checks, repair restoring latest values, writes failing after paranoid compaction corruption, and unrelated keys remaining usable after a corrupt table.
