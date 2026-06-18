## sources/user-network-fs/gcsfuse/internal/gcsx/mrd_pool_test.go

Purpose: unit tests for `MRDPool` construction, sizing, round-robin selection, recreation, and close behavior.

Important APIs and fixtures: `mrdPoolTest`, `MRDPoolConfig`, mock bucket, fake MRDs with handles, and table-driven pool-size cases.

Control flow and behavior covered: small and large file initialization, async creation failure tolerance, file-clobbered conversion for initial not-found, nil config error, generic creation error, `Next` round-robin over initialized entries, size determination thresholds, `RecreateMRD` using current, fallback, or peer handles, recreate failure, `Close` waiting/closing entries and returning a handle, and verifying `Close` does not cancel the downloader creation context.

State/persistence signals: tests inspect `entries`, `currentSize`, `current`, downloader handles, and niling after close. Async creation tests wait for creation goroutines to complete before assertions.

Dependencies/integration: uses storage mock bucket, fake multi-range downloaders, `testify/suite`, and GCS request matchers.

Risks/test signals: good unit coverage for pool mechanics. It does not deeply stress concurrent `Next` and `RecreateMRD`, but implementation uses atomics and entry locks for that path.
