# sources/user-network-fs/gcsfuse/internal/storage/fake_storage_util.go

## Purpose
This file provides a reusable fake-storage fixture for storage-layer tests. It starts `fake-gcs-server` with a fixed bucket/object dataset and returns a `StorageHandle` backed by the fake server's client plus an optional mocked storage control client.

## Important APIs and State
Constants define the default test bucket, object names, folder-like prefixes, generation numbers, metadata keys, and a compressed gzip test object. `FakeStorage` exposes `CreateStorageHandle` and `ShutDown`. `fakeStorage` stores the fake server, optional `MockStorageControlClient`, and selected `cfg.Protocol`. `NewFakeStorage` creates a default fixture; `NewFakeStorageWithMockClient` injects a control-client mock and protocol. `getTestFakeStorageObject` builds the initial object list, including root/subroot folder markers, a regular object with metadata, a subobject, and a gzip-encoded object. `createFakeStorageServer` delegates to `fakestorage.NewServerWithOptions`.

## Control Flow and Integration
`CreateStorageHandle` lazily creates a mock control client if absent and constructs a `storageClient` whose HTTP, gRPC, and bidi-gRPC clients all point at the fake server client. The returned handle uses `storageutil.StorageClientConfig` with the configured protocol and an empty write config. This fixture integrates with tests that expect the production `StorageHandle` interface while avoiding real GCS calls.

## Risks and Test Signals
The fixture panics on fake-server creation failures, which is acceptable for test setup but unsuitable for production. Because one fake server client backs all protocol slots, protocol-specific behavior may not be faithfully represented. The fixed gzip byte string is fragile: changing compressed bytes requires synchronizing the documented decompressed content. `ShutDown` must be called to stop the server.
