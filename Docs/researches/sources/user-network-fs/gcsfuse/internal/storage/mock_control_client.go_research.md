# sources/user-network-fs/gcsfuse/internal/storage/mock_control_client.go

## Purpose
This file defines a testify mock for the storage control client used by HNS folder APIs and bucket storage-layout lookup.

## Important APIs and Control Flow
`MockStorageControlClient` embeds `StorageControlClient` and `mock.Mock`. It implements `GetStorageLayout`, `DeleteFolder`, `GetFolder`, `CreateFolder`, and `RenameFolder`. Each method calls `m.Called(ctx, req, opts)` and returns configured proto/operation values or errors. Folder-returning methods use type assertions to allow nil/error cases.

## State, Dependencies, and Integration
State is in the embedded mock. Dependencies include standard `context`, storage control client/protos, `gax`, and `testify/mock`. `fake_storage_util.go` can inject this mock into a fake `StorageHandle`, and storage-handle tests can assert control-client calls without real Storage Control API traffic.

## Risks and Test Signals
Call expectations include the variadic `opts` slice as a single argument, so tests must match that shape. `GetStorageLayout` assumes a non-error success return is a `*controlpb.StorageLayout`, and will panic if nil or wrong typed. The mock covers only the subset of `StorageControlClient` used by current code.
