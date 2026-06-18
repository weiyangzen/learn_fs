# sources/storage-engines/rocksdb/monitoring/thread_status_util.h

Purpose: Declares the public internal utility class for updating current-thread RocksDB status without exposing direct updater management at every call site.

Important APIs/types/functions: `ThreadStatusUtil` static methods cover thread registration, CF info lifecycle, tracking enablement, current CF, operation, operation stage/properties, state, reset, debug delays, and expected IO-activity mapping. `AutoThreadOperationStageUpdater` is an RAII helper for temporary stage changes.

Control flow/integration: DB, compaction, flush, Env, and iterator code can call these methods to update thread status. The utility lazily caches an Env-provided `ThreadStatusUpdater` per thread and no-ops when tracking is disabled or unavailable.

State and dependencies: Declares thread-local updater cache and initialization flag in enabled builds; disabled builds use static globals. Depends on DB, Env, thread-status public API, and updater declarations.

Risks/test signals: Static thread-local cache makes lifecycle order important. API comments require CF map updates without holding `db_mutex`. Debug-only methods support deterministic mutex/state-delay tests.
