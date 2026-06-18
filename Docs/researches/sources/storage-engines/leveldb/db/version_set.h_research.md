# sources/storage-engines/leveldb/db/version_set.h

Purpose: declares the metadata model for LevelDB versions, version sets, and compactions.

Important APIs and types: free functions `FindFile` and `SomeFileOverlapsRange`; class `Version` with `GetStats`, `AddIterators`, `Get`, `UpdateStats`, `RecordReadSample`, `Ref`, `Unref`, `GetOverlappingInputs`, `OverlapInLevel`, `PickLevelForMemTableOutput`, `NumFiles`, and `DebugString`; class `VersionSet` with `LogAndApply`, `Recover`, file-number/sequence accessors, compaction selectors, live-file enumeration, `ApproximateOffsetOf`, and `LevelSummary`; class `Compaction` with input accessors, `IsTrivialMove`, `AddInputDeletions`, `IsBaseLevelForKey`, `ShouldStopBefore`, and `ReleaseInputs`.

Control flow: callers interact with `VersionSet::current()` and `Version` references to protect metadata while iterators and reads run. Compactions are selected by score or seek pressure and represented as two input vectors from adjacent levels.

State and persistence behavior: `VersionSet` owns database name, options, table cache, internal comparator, MANIFEST writer/file, version list, current version pointer, file/log/sequence counters, and per-level compaction pointers. `Version` owns per-level `FileMetaData*` vectors and compaction score hints.

Dependencies and integration: bridges internal format, table cache, manifest logging, environment files, DB mutexes, and compaction code. The header documents thread-compatibility: external synchronization is required for all accesses.

Risks and edge cases: consumers must maintain reference counts correctly or files/versions can be freed under iterators. `LogAndApply` requires the DB mutex on entry and no concurrent callers. Levels above 0 require non-overlapping sorted files.

Test signals: declarations are exercised by version-set, recovery, DB, and compaction tests.
