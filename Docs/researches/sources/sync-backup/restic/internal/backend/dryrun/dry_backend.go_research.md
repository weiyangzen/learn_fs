# sources/sync-backup/restic/internal/backend/dryrun/dry_backend.go

Purpose: Implements a write-suppressing backend wrapper used by `backup --dry-run`.

Important APIs and types: `Backend` wraps an underlying `backend.Backend`. `New` constructs it. `Save`, `Remove`, and `Delete` validate/accept but do not mutate the repository. `Properties`, `Close`, `Hasher`, `IsNotExist`, `IsPermanentError`, `List`, `Load`, and `Stat` delegate. `Warmup` and `WarmupWait` are no-ops.

Control flow and state: Mutating operations return nil without touching the wrapped backend, except `Save` first validates the handle. Read-only operations pass through to the underlying backend. There is no local persistent state.

Dependencies and integration: Depends on `backend` and `debug`. It layers over any real backend for dry-run mode so backup logic can read repository state while avoiding modifications.

Risks and test signals: Risks include accidental mutation leakage, invalid handles being accepted, or warmup causing side effects during dry run. `dry_backend_test.go` verifies that saves/removes/deletes do not affect the underlying memory backend while reads/lists/stats still work.
