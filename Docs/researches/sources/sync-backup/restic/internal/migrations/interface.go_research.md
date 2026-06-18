## sources/sync-backup/restic/internal/migrations/interface.go

Purpose: defines the common migration contract.

Important APIs/types: `Migration` requires `Check(context.Context, restic.Repository) (bool, string, error)`, `RepoCheck() bool`, `Apply(context.Context, restic.Repository) error`, `Name() string`, and `Desc() string`.

Control flow and state: the interface itself is stateless; implementations decide applicability, whether repository checks are required, and how to mutate repository/backend state.

Dependencies and integration points: depends on `context` and `restic.Repository`. Command code can use this interface over the registered `All` slice.

Risks and test signals: `Apply` accepts the broad `restic.Repository` interface, but implementations may type-assert to concrete repository types, so callers must pass compatible implementations. Tests currently cover the v2 upgrade migration.
