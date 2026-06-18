# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compaction_service.h

- **Purpose:** Declares and mostly implements a simulated remote `CompactionService` for db_stress.
- **Important APIs/types/functions:** Defines `DbStressCompactionService`, `kClassName`, `Name`, `kWaitIntervalInMicros`, `kTempOutputDirectoryPrefix`, `Schedule`, `Wait`, `OnInstallation`, and `CancelAwaitingJobs`.
- **Control flow:** `Schedule` builds a job ID and temp output path, enqueues work in `SharedState`, and returns success unless aborted. `OnInstallation` reads the serialized result, deletes output files/directories, and removes the result from shared state. `CancelAwaitingJobs` sets the abort flag.
- **State and persistence behavior:** Holds `SharedState*`, atomic abort state, and fallback policy. Creates temp output directory names and cleans output directories through `Env::Default`; actual compaction output is produced by worker threads.
- **Dependencies and integration points:** Depends on compaction job/service APIs, `SharedState`, options, and fault-injection headers. Paired with `RemoteCompactionWorkerThread` in `db_stress_common.cc`.
- **Risks:** Cleanup is best-effort and TODO-marked on failure. Job IDs combine DB identity/session/job values and must stay unique. Aborted service sends new jobs to local compaction and waiting jobs to aborted.
- **Test signals:** Remote compaction queue/result counts, cleanup of temp output dirs, fallback status under abort/failure, and stress verification after compaction installation.
