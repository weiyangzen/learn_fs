# sources/sync-backup/kopia/repo/blob/retrying/retrying_storage.go

Purpose: wraps blob storage operations in exponential backoff for transient/unexpected errors.

Important APIs/types/functions: `retryingStorage`, `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `NewWrapper`, and `isRetriable`.

Control flow: each wrapped data operation calls `retry.WithExponentialBackoff` or `WithExponentialBackoffNoValue`, delegates to the base storage, and retries only when `isRetriable` returns true. `GetBlob` resets the output buffer before every attempt to avoid mixed partial data. Non-retriable errors include not found, invalid range, set-time unsupported, invalid credentials, unsupported put option, already exists, and repository unavailable due to upgrade.

State and persistence behavior: wrapper state is only the embedded storage reference. Retried `PutBlob`/`DeleteBlob` can repeat external side effects, so underlying operations must be idempotent or translate permanent errors correctly.

Dependencies/integration points: used by cloud providers and other adapters to smooth transient failures. Risks include retrying non-idempotent operations when providers return unexpected errors, hiding latency, and not wrapping list/capacity/close operations. Tests cover retry behavior and non-retriable classification in representative paths.
