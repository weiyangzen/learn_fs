# sources/storage-engines/leveldb/db/version_set.cc

Purpose: implements LevelDB's version graph, MANIFEST recovery/application, file lookup, read routing, compaction selection, and compaction input expansion. It is the core metadata manager for the LSM tree.

Important APIs and functions: `FindFile`, `SomeFileOverlapsRange`, `Version::AddIterators`, `Get`, `UpdateStats`, `RecordReadSample`, `GetOverlappingInputs`, `PickLevelForMemTableOutput`, `DebugString`, `VersionSet::LogAndApply`, `Recover`, `ReuseManifest`, `WriteSnapshot`, `Finalize`, `PickCompaction`, `CompactRange`, `SetupOtherInputs`, `MakeInputIterator`, `AddBoundaryInputs`, `FindSmallestBoundaryFile`, `Compaction::IsTrivialMove`, `AddInputDeletions`, `IsBaseLevelForKey`, and `ShouldStopBefore`.

Control flow: reads search level 0 overlapping files newest first, then binary-search one file per nonzero level. Version edits are applied by `Builder`, which merges base files with added/deleted files and asserts non-overlap for levels above 0. `LogAndApply` builds a new version, writes a snapshot if opening a new MANIFEST, appends the edit, syncs, updates `CURRENT` if needed, and installs the version. `Recover` reads `CURRENT`, replays MANIFEST records, validates comparator name, reconstructs a version, and either reuses or requests compaction of the manifest.

State and persistence behavior: persistent state is a sequence of encoded `VersionEdit` records in MANIFEST files plus `CURRENT` pointing at the active manifest. In-memory state includes a circular list of live versions, current file/log/sequence counters, per-level compact pointers, file reference counts, and compaction scores. Compaction edits delete inputs and add outputs elsewhere in DB implementation.

Dependencies and integration: depends on file naming, log reader/writer, table cache, table iterators, merging/two-level iterators, internal key comparator, memtable/table builder APIs, `Env`, and `Options`. `DBImpl` calls this for open, reads, writes, compaction scheduling, live-file cleanup, and approximate sizes.

Risks and edge cases: descriptor writes unlock the DB mutex, so callers must obey the no-concurrent-`LogAndApply` precondition. Boundary-file expansion is critical: omitting it can make older records for the same user key win after compaction. Level-0 overlap expansion can grow inputs by restarting range discovery. Reuse of manifests depends on append support and size threshold. File number reuse and stale cache entries must be coordinated with table-cache eviction.

Test signals: `version_set_test.cc` covers `FindFile`, overlap checks, and boundary input expansion. `recovery_test.cc` covers recover/reuse paths. Many DB tests indirectly cover compaction and lookup.
