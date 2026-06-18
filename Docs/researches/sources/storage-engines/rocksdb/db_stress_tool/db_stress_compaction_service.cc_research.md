# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compaction_service.cc

- **Purpose:** Implements waiting/result interpretation for the db_stress remote compaction service.
- **Important APIs/types/functions:** Implements `DbStressCompactionService::Wait`.
- **Control flow:** Polls `SharedState::GetRemoteCompactionResult` until a result appears or the service is aborted. Successful results return `kSuccess`; failures may fall back to local compaction when configured or retryable, otherwise serialize the failure into a `CompactionServiceResult` and return `kFailure`.
- **State and persistence behavior:** Reads remote compaction result state from `SharedState`; writes serialized failure details into the caller-provided result string when needed. Sleeps through `Env::Default`.
- **Dependencies and integration points:** Includes the service header, `db_stress_test_base.h`, and `rocksdb/env.h`; used by RocksDB compaction service callbacks configured during stress tests.
- **Risks:** Wait is polling-based and depends on worker threads publishing results. Empty result strings on failure need successful serialization to propagate status. Abort returns before late results are installed.
- **Test signals:** Compaction service status (`kSuccess`, `kUseLocal`, `kFailure`, `kAborted`), fallback behavior under injected retryable errors, and primary DB compaction completion.
