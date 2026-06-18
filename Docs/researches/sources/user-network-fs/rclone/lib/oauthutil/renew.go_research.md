# sources/user-network-fs/rclone/lib/oauthutil/renew.go

Source read signal: reviewed complete local file (94 lines, sha256 9b5ebc7fdc68f8fa).

Purpose: Keeps OAuth tokens refreshed while long-running uploads are active.

Important APIs/types/functions: Type `Renew` with constructor `NewRenew` and methods `Start`, `Stop`, `Invalidate`, `Expire`, and `Shutdown`.

Control flow: `NewRenew` starts `renewOnExpiry`, which waits on `TokenSource.OnExpiry` or shutdown. When expiry fires and upload count is nonzero, it runs the supplied transaction to refresh; otherwise it logs and does nothing. `Start`/`Stop` adjust an atomic upload counter.

State and persistence behavior: Holds upload count, done channel, shutdown once, and a pointer to `TokenSource`. Refresh side effects are delegated to `run` and token source persistence.

Dependencies and integration points: Uses `sync`, `atomic`, and rclone logging. Used by backends whose providers may cancel uploads if tokens are not refreshed during transfer.

Risks and test signals: `Shutdown` stops `ts.expiryTimer` only if it exists; nil handling for receiver is present. Upload counter can go negative if `Stop` is unbalanced. Tests should cover expiry with active/inactive uploads and idempotent shutdown.
