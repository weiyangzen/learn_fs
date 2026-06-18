# sources/sync-backup/git-lfs/lfsapi/client.go

Purpose: Exposes `lfsapi.Client` methods that delegate generic HTTP behavior to the embedded `lfshttp.Client`.

Important APIs/types/functions: `NewRequest`, `Do`, `do`, `doWithAccess`, `LogRequest`, `GitEnv`, `OSEnv`, `ConcurrentTransfers`, `LogHTTPStats`, and `Close`.

Control flow: Most methods are pass-through wrappers. `Close` joins errors from shutting down pure SSH transfers and closing the HTTP client/logging resources.

State and persistence behavior: Delegates state to `lfshttp.Client` and SSH transfer map in `lfsapi.Client`. `Close` clears SSH transfers through `closeSSHTransfers`.

Dependencies and integration points: Integrates the API client abstraction with `lfshttp`, `config.Environment`, `creds.AccessMode`, and shared `errors.Join`.

Risks and edge cases: Wrapper methods preserve API shape while allowing auth layer to call generic HTTP routines. `do` currently ignores `remote` and `via`, relying on lower layers for redirects.

Test signals: Behavior is covered indirectly by auth, response, endpoint, and locking tests.
