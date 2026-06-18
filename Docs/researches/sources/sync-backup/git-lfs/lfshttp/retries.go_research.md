# sources/sync-backup/git-lfs/lfshttp/retries.go

Purpose: Stores per-request network retry counts in request context.

Important APIs/types/functions: `ckey`, `contextKeyRetries`, `defaultRequestRetries`, `WithRetries`, and `Retries`.

Control flow: `WithRetries` returns a cloned request with retry count in context. `Retries` reads and type-asserts the value.

State and persistence behavior: Request context carries retry state in memory. No global state.

Dependencies and integration points: Used by `Client.DoWithRedirect` to retry network errors and rewind seekable bodies. Default retries are zero unless annotated.

Risks and edge cases: Negative retry counts are normalized by caller with `max(0, retries)`. Non-seekable bodies may not replay correctly on retry.

Test signals: `retries_test.go` covers context storage, absence, and successful retry of a POST body after dropped connections.
