# sources/user-network-fs/gcsfuse/internal/storage/control_client_wrapper.go

## Purpose
`control_client_wrapper.go` defines the local abstraction and wrappers for Google Cloud Storage Control API calls used by gcsfuse. It adds billing-project metadata, gcsfuse-level retry behavior, and raw gax retry options for folder APIs.

## Important APIs, Types, and Functions
`StorageControlClient` is the narrow interface for `GetStorageLayout`, `DeleteFolder`, `GetFolder`, `RenameFolder`, and `CreateFolder`. `storageControlClientWithBillingProject` wraps a client and appends `x-goog-user-project` metadata to most calls. `storageControlClientWithRetry` wraps a client with `storageutil.RetryConfig` and flags that control whether retries apply only to storage layout or to all folder APIs too.

Factory helpers are `withBillingProject`, `newRetryWrapper`, `withRetryOnAllAPIs`, and `withRetryOnStorageLayout`. `storageControlClientGaxRetryOptions` builds gax timeout/retry call options. `addGaxRetriesForFolderAPIs` mutates a raw `control.StorageControlClient` call-options struct to apply retries to folder operations.

## Control Flow
Billing-project wrapping appends outgoing gRPC metadata for `GetStorageLayout`, `DeleteFolder`, `GetFolder`, and `CreateFolder`; `RenameFolder` intentionally uses the original context because the long-running operation path does not support that billing header.

Retry wrapping checks enable flags per method. If disabled, it directly delegates. If enabled, it builds an attempt closure that calls the raw client with an attempt context and passes it to `storageutil.ExecuteWithRetry` or `ExecuteWithRetryAtLogLevel`. Request descriptions use bucket/folder names and are included in retry logging/error context. `newRetryWrapper` unwraps an existing retry wrapper before constructing a new one to avoid nested retry loops.

Gax retry options apply `DefaultTotalRetryBudget` as timeout and retry on `ResourceExhausted`, `Unavailable`, `DeadlineExceeded`, `Internal`, `Unknown`, and temporarily `Unauthenticated`. Folder gax retries are installed in place after validating both raw client and client config are non-nil and `CallOptions` is initialized.

## State and Persistence Behavior
The wrappers are lightweight in-memory decorators. They retain a raw client pointer, billing-project string, retry config pointer, and retry-enable booleans. No state is persisted, but retry behavior affects timing, call repetition, and context cancellation.

## Dependencies and Integration Points
The code depends on `cloud.google.com/go/storage/control/apiv2`, generated `controlpb` messages, `gax`, gRPC status codes, `metadata.AppendToOutgoingContext`, `logger`, and `storageutil` retry configuration. It integrates with bucket construction code that needs HNS storage layout and folder APIs.

## Risks and Edge Cases
Retry policy correctness is the key risk. Retrying non-idempotent or long-running folder operations can duplicate requests if server semantics are not safe; this is gated by `retryFolderAPIs` and gax configuration. `RenameFolder` omits the billing project by design, which can surprise callers expecting all API calls to carry it. `addGaxRetriesForFolderAPIs` resets the whole call-options struct, so future call options could be accidentally cleared. Including `Unauthenticated` as retryable is marked temporary and should be revisited.

## Test Signals
`control_client_wrapper_test.go` covers success, retryable error recovery, non-retryable errors, timeout behavior, methods that should not retry in storage-layout-only mode, wrapper unnesting, gax option shape, unauthenticated retryability, and invalid raw-client inputs.
