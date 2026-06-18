# sources/sync-backup/git-lfs/tq/transfer.go

Purpose: core transfer domain types and adapter interfaces.

Important APIs/types/functions: `Direction` with `Upload`, `Download`, `Checkout`; `Progress`/`String`; `Transfer`; `Rel`; `ObjectError`; `newTransfer`; `Action`; `IsExpiredWithin`; `ActionSet.Get`; `ActionExpiredErr`; `IsActionExpiredError`; `NewAdapterFunc`; `ProgressCallback`; `AdapterConfig`; `Adapter`; and `TransferResult`.

Control flow: `Transfer.Rel` checks actions then links for a relation and returns nil if absent. `ActionSet.Get` rejects actions expiring within five seconds by returning a retriable `ActionExpiredErr`. `newTransfer` deep-copies transfer metadata/actions for queue processing.

State and persistence: pure in-memory API types mirroring JSON batch data plus local-only fields (`Path`, `Missing`, action creation time).

Dependencies and integration points: used by all transfer queue and adapter code; integrates with `lfsapi.Client`, `tools` time helpers, and translated messages.

Risks: `IsActionExpiredError` only matches `*ActionExpiredErr`, while `ActionSet.Get` constructs `&ActionExpiredErr` wrapped in retriable error; callers usually use generic retriable checks. Action expiry depends on `createdAt` being set by batch clients.

Test signals: `transfer_test.go` focuses on adapter registration via manifest, not these data methods directly.
