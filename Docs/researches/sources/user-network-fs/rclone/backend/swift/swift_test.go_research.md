# sources/user-network-fs/rclone/backend/swift/swift_test.go

Purpose: Swift backend integration/internal tests. It runs `fstests.Run` against `TestSwiftAIO:` and adds backend-specific coverage for unchunked streaming, segmented uploads, failed segmented upload cleanup, large-object copy, and storage policy discovery.

Important APIs: `TestIntegration`, `SetUploadChunkSize`, `InternalTest`, `testNoChunk`, `testWithChunk`, `testWithChunkFail`, `testCopyLargeObject`, and `testPolicyDiscovery`. These mutate `f.opt.NoChunk`, `ChunkSize`, `StoragePolicy`, and `UseSegmentsContainer`, restoring state with defers.

Control flow/state: tests build `fstest.Item` objects with unknown size (`-1`) to exercise `PutStream`; check hashes, rereads, usage accounting, and object removal; inject an `ErrorReader` to verify failed chunked uploads leave no final object or stray segments; and verify segment-container storage policy inheritance.

Dependencies/integration: `github.com/ncw/swift/v2`, rclone `fs/hash/object/fstest/fstests`, random/readers helpers, and testify. These tests require a configured Swift all-in-one remote and inspect backend internals such as `f.c`, root container, segment container, and policy fetch.

Risks/test signals: strong signals for cleanup, quota deltas, large-object copy size, and storage policy propagation, but most coverage is live-environment dependent.
