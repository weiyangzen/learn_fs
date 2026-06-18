# sources/user-network-fs/blobfuse2/component/azstorage/connection.go

## Purpose
Defines the storage backend configuration object, the common `AzConnection` interface implemented by block-blob and ADLS backends, and the factory that selects the correct concrete connection for an account type.

## Important APIs, Types, and Functions
`AzStorageConfig` is the internal parsed configuration shared by storage implementations. It embeds `azAuthConfig` and stores container, prefix path, transfer sizing, default access tier, mount-time list blocking, retry policy, proxy address, unsupported-operation behavior, mount-all-containers, MD5 flags, virtual-directory settings, list page size, compression, telemetry, ACL behavior, CPK key material, optional `blobfilter.BlobFilter`, and read/IOPS caps.

`AzStorageConnection` is a small base struct containing `Config AzStorageConfig`. `AzConnection` is the backend contract: lifecycle/config methods (`Configure`, `UpdateConfig`, `SetupPipeline`, `TestPipeline`, `UpdateServiceClient`, `SetPrefixPath`, `SetFilter`), account/container methods, namespace methods, file IO methods, write/block-list methods, POSIX modifier methods, and block-list staging/commit methods. `NewAzStorageConnection()` returns a configured `*BlockBlob` for block accounts, a configured `*Datalake` for ADLS accounts, logs invalid account types, and returns nil when no valid implementation matches.

## Control Flow, State, and Persistence
The factory is intentionally simple: inspect `cfg.authConfig.AccountType`, allocate the selected backend, call its `Configure(cfg)` method, ignore the returned error, and return the backend pointer. The connection state is persisted in the concrete backend's embedded config and clients after later `SetupPipeline()` calls. The interface makes no distinction between operations natively implemented by the backend and operations delegated to another backend, which is important because `Datalake` implements many file/block operations by forwarding to an embedded `BlockBlob`.

## Dependencies and Integration Points
Depends on Azure SDK blob access-tier types, Blobfuse `common.BlockOffsetList`, `internal.ObjAttr`, `internal.WriteFileOptions`, `internal.TruncateFileOptions`, logging, and `blobfilter`. This file is the contract boundary between `AzStorage` component methods in `azstorage.go` and concrete storage implementations in `block_blob.go` and `datalake.go`. Any new backend must satisfy every method in `AzConnection`, including test-only `SetPrefixPath`.

## Risks and Test Signals
The main risks are interface breadth, ignored `Configure()` errors in the factory, nil returns for invalid account types, and tight coupling of high-level component behavior to backend-specific block-list semantics. Because `AzConnection` includes both blob-native and POSIX-like operations, additions require changes across all implementations. Test signals come indirectly from `block_blob_test.go`, `config_test.go`, and ADLS-specific tests elsewhere: they verify factory selection through account type config, block/ADLS behavior, and dynamic config updates.
