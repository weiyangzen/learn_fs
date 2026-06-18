# sources/sync-backup/git-lfs/git/refs_test.go

Purpose: unit tests for `RefUpdate` remote-ref derivation and commitish behavior.

Important APIs/types/functions: `NewRefUpdate`, `ParseRef`, `LocalRefCommitish`, `RemoteRef`, `RemoteRefCommitish`, and `mapEnv`.

Control flow: table-like loops create map-backed config and assert the derived remote ref name/type for `push.default` variants. Explicit refs test SHA-vs-name commitish output.

State/persistence behavior: in-memory config only.

Dependencies/integration: validates behavior used by LFS transfer queue remote-ref selection.

Risks/test signals: does not cover unsupported push.default values or nil local refs.
