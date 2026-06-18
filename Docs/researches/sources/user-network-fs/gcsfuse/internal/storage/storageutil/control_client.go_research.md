## sources/user-network-fs/gcsfuse/internal/storage/storageutil/control_client.go

Purpose: Creates a Google Storage Control gRPC client with optional default GAX retries disabled.

Important APIs/types/functions: `CreateGRPCControlClient(ctx, clientOpts, disableDefaultGaxRetries)` sets `GOOGLE_CLOUD_ENABLE_DIRECT_PATH_XDS`, calls `control.NewStorageControlClient`, optionally replaces `CallOptions` with an empty `StorageControlCallOptions`, then unsets the environment variable.

Control flow: environment is set before client construction and unset after successful setup. On client creation failure it returns wrapped error before reaching the unset call.

State and persistence behavior: mutates process environment. This is transient on success, but the error path can leave direct-path XDS enabled because unset happens after successful client creation.

Dependencies and integration points: used by storage handle creation for raw control clients with and without GAX retries. Depends on Google Storage Control v2 generated client and internal logger fatal behavior for env mutation failures.

Risks: process-wide environment mutation is not concurrency-safe and has an error-path leakage risk. Emptying `CallOptions` changes retry behavior for folder and layout APIs and must match wrapper retry logic.

Test signals: `control_client_test.go` verifies default call options are populated and disabled options are empty when requested.
