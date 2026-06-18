## sources/user-network-fs/gcsfuse/internal/gcsx/mrd_instance_test.go

Purpose: comprehensive unit tests for `MrdInstance` read, pool, refcount, cache, eviction, and generation-update behavior.

Important APIs and fixtures: `MrdInstanceTest`, mock bucket, fake MRDs, LRU cache, config with MRD pool size, and log capture helpers for timeout warning verification.

Control flow and behavior covered: constructor fields, successful reads, lazy pool initialization, invalid MRD recreation, ensure/recreation failures, empty buffer, context cancellation, MRD add errors, `getMRDEntry`, `RecreateMRD`, `Destroy`, refcount increment/decrement, cache insertion/removal, eviction behavior, key formatting, pool size reporting, cache insert failure, `closePool`, eviction races, `createAndSwapPool`, nil/same/different generation `SetMinObject`, and `GetMinObject`.

State/persistence signals: tests inspect `mrdPool`, refcount, cache membership, object generation updates, and asynchronous close timeout logging. They validate reopening removes an instance from inactive cache and preserves pool reuse when safe.

Dependencies/integration: uses storage mock bucket, fake MRDs, LRU cache package, config, logger capture, and `testify/suite`.

Risks/test signals: strong coverage for lock-sensitive lifecycle paths, including resurrected and re-added cache entries. Some close behavior is asynchronous and verified with sleeps, so timing can be a residual flake risk.
