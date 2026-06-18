# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compaction_filter.h

- **Purpose:** Provides a db_stress compaction filter that removes or purges keys known to be absent in `SharedState`, without mutating state during compaction.
- **Important APIs/types/functions:** Defines `DbStressCompactionFilter : CompactionFilter` with `FilterV2` and `Name`; defines `DbStressCompactionFilterFactory : CompactionFilterFactory` with `SetSharedState`, `CreateCompactionFilter`, and `Name`.
- **Control flow:** `FilterV2` keeps keys when no shared state is available, when keys look like batched-snapshot leftovers, or when the per-key mutex cannot be acquired. Otherwise it decodes the key number, checks expected existence/overwrite policy under the key mutex, and returns `kRemove`, `kPurge`, or `kKeep`.
- **State and persistence behavior:** Reads `SharedState` expected key state but does not mutate it. Compaction decisions affect persisted SST output by dropping keys/tombstones.
- **Dependencies and integration points:** Depends on `db_stress_common.h`, `db_stress_shared_state.h`, and `rocksdb/compaction_filter.h`; configured in db_stress options when compaction-filter stress is enabled.
- **Risks:** Key decoding assumes the db_stress key format and user timestamp suffix size. A failed `TryLock` conservatively keeps keys, reducing filter coverage. Current TODO notes lack of wide-column blob entity coverage for newer filter APIs.
- **Test signals:** Stress verification should remain consistent after compactions; assertions catch timestamp/key decoding issues; coverage should include overwrite and no-overwrite expected-state modes.
