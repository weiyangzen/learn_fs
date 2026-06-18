<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/channels.go -->
# sources/sync-backup/git-lfs/tools/channels.go

Purpose: provides a small abstraction for asynchronous result channels that also expose deferred error collection.

Important APIs/types/functions: `ChannelWrapper` interface, `BaseChannelWrapper`, `NewBaseChannelWrapper`, and `(*BaseChannelWrapper).Wait`.

Control flow: `Wait` drains `errorChan` until closed, joining all received errors with Git LFS's `errors.Join`, then returns the combined error.

State and persistence: in-memory error channel only; no persistent state.

Dependencies and integration points: depends on `github.com/git-lfs/git-lfs/v3/errors`. Intended for iterator/result-channel producers that report async errors after consumers finish reading results.

Risks: callers must drain result channels before `Wait` and producers must close the error channel. Otherwise `Wait` can block indefinitely.

Test signals: no direct test in this subset; behavior is simple and likely covered by users of channel wrappers elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/channels.go -->
