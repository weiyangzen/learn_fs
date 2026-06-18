# sources/sync-backup/git-lfs/git/refs.go

Purpose: models a push ref update, deriving the remote destination ref from Git config and local ref when not explicitly supplied.

Important APIs/types/functions: `RefUpdate`, `NewRefUpdate`, `LocalRef`, `LocalRefCommitish`, `RemoteRef`, `defaultRemoteRef`, `TrackingRef`, `RemoteRefCommitish`, and `Env`.

Control flow: `RemoteRef` lazily computes a default using `push.default`. `simple` and empty use tracking ref only when branch remote matches target remote, otherwise current branch. `upstream`/`tracking` use branch merge config. `current` uses local ref. Unsupported modes log a warning and fall back to local ref.

State/persistence behavior: read-only access to config via `Env`. The computed remote ref is cached on the `RefUpdate`.

Dependencies/integration: used by `GitFilter.RemoteRef` to set transfer queue remote-ref metadata during smudge/download.

Risks/test signals: support is intentionally partial for push.default modes; unsupported modes silently degrade with trace logging. Tests cover default, tracking, current, and explicit refs.
