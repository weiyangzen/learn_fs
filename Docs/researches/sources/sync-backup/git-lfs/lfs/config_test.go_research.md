# sources/sync-backup/git-lfs/lfs/config_test.go

Purpose: tests default and custom `FetchPruneConfig` construction.

Important APIs/types/functions: `NewFetchPruneConfig`, `config.NewFrom`, and `testify/assert`.

Control flow: one test constructs empty config and asserts defaults; another supplies Git config values and asserts parsed overrides.

State/persistence behavior: in-memory config only.

Dependencies/integration: guards environment reporting and fetch/prune behavior from silent default changes.

Risks/test signals: does not test invalid integer/boolean parsing or command-layer overrides for `PruneRecent` and `PruneForce`.
