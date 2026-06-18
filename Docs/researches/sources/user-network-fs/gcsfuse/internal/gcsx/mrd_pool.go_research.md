## sources/user-network-fs/gcsfuse/internal/gcsx/mrd_pool.go

Purpose: manages a round-robin pool of `gcs.MultiRangeDownloader` instances for concurrent reads of one GCS object.

Important APIs/types/functions: `MRDEntry`, `MRDPoolConfig`, `MRDPool`, `determinePoolSize`, `NewMRDPool`, `createRemainingMRDs`, `Next`, `RecreateMRD`, `Close`, and `Size`.

Control flow: pool size is reduced to 1 for objects below 100 MiB and 2 for objects below 500 MiB, otherwise configured size remains. `NewMRDPool` creates the first downloader synchronously, maps initial `NotFoundError` to `FileClobberedError`, stores current size, and creates remaining downloaders asynchronously using the first downloader’s handle. `Next` round-robins over initialized entries. `RecreateMRD` locks one entry and obtains a handle from that entry, fallback handle, or a peer via `TryRLock`. `Close` stops background creation, waits for it, waits for in-flight downloads, captures a handle, closes downloaders, and nils entries.

State/persistence behavior: in-memory entries, atomics for next/current size, background creation control channel, and wait group. It maintains remote read handles but no local data.

Dependencies/integration: GCS MRD API, file-clobbered error type, logger, atomics, and sync primitives. Used by `MrdInstance`.

Risks/test signals: if asynchronous creation fails, `currentSize` still increases, leaving nil entries that callers must recreate. Closing `stopCreation` twice would panic, so `Close` should be single-use. Tests cover sizing, async creation failure, file clobber, round robin, handle selection, recreation errors, close semantics, and context non-cancellation.
