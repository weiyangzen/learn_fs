<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_prune.go -->
# sources/sync-backup/git-lfs/commands/command_prune.go

Purpose: implements `git lfs prune`, identifying local LFS objects not retained by refs, recent history, unpushed commits, worktrees, stash, or index state, optionally verifying remote presence before deleting them.

Important APIs/types/functions: prune flag globals; `pruneCommand`, `PruneProgressType`, `PruneProgress`, `prune`, `logVerboseOutput`, `pruneGetVerifiedPrunableObjects`, `pruneCheckErrors`, progress/error/retained collector tasks, `pruneDeleteFiles`, and scanner tasks for local objects, refs, previous versions, unpushed, worktrees, stash, index, and reachable objects.

Control flow: parses verification and force/recent flags into `FetchPruneConfig`, launches goroutines to collect local objects and retained OIDs from several Git sources, uses a semaphore to bound scanner concurrency, gathers errors, computes prunable OIDs, optionally enqueues download-check transfers to verify remote presence, filters unverified objects according to reachability and `--verify-unreachable`, reports progress/verbose output, and deletes object files unless dry-run.

State and persistence behavior: deletes media files from `.git/lfs/objects` by OID in non-dry mode, reads all local object metadata, and may query remote download endpoints in dry-run check mode. It does not update refs.

Dependencies/integration points: integrates GitScanner APIs, worktree/stash/index/ref scanning, LFS object filesystem, tasklog progress, transfer queues, config retention windows, and fetch `--prune`.

Risks and test signals: risks include concurrent use of a shared GitScanner across goroutines, semaphore acquire errors ignored, verify logic depending on remote download check semantics, force/recent retention interactions, and deleting by OID without retry. Test signals include dry-run, verbose, recent/force, verify remote reachable/unreachable, unpushed retention, worktree/index/stash retention, remote missing halt/continue, and deletion failure handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_prune.go -->
