# sources/sync-backup/syncthing/lib/config/commit_test.go

## sources/sync-backup/syncthing/lib/config/commit_test.go

Purpose: Tests the `config.Wrapper` commit pipeline, especially validation rejection, subscriber commit notification, and restart-required propagation.

Important APIs/types/functions: `requiresRestart` implements both `Verifier` and `Committer`, returning `false` from `CommitConfiguration`; `validationError` rejects via `VerifyConfiguration`; `replace` wraps `Wrapper.Modify`; `TestReplaceCommit` exercises `RawCopy`, `Modify`, `Subscribe`, waiter synchronization, and `RequiresRestart`.

Control flow and state: A wrapper is started around an initial `Configuration{Version: 0}`. `Modify` queues replacement, `replaceLocked` prepares/migrates it to `CurrentVersion`, verifiers run before committers, and committers can set the atomic restart flag without blocking the config change. When a verifier returns an error, the config remains unchanged while any previous restart-required state remains set.

Dependencies and integration: Uses local test helpers from `config_test.go` (`wrap`, `testWrapper.stop`) and the production `Wrapper` interface. The test is a direct contract for consumers that subscribe to configuration changes.

Risks and test signals: The key risk is deadlock or partial state update in the config notification path. The test confirms waiter completion, verifier short-circuiting, and that restart-required is sticky after a subscriber requests it.
