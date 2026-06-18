<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_fetch.go -->
# sources/sync-backup/git-lfs/commands/command_fetch.go

Purpose: implements `git lfs fetch`, scanning refs/history for LFS pointers and downloading missing media objects, with options for all refs, recent refs/commits, pruning, dry-run/refetch, JSON output, and refs from stdin.

Important APIs/types/functions: `fetchWatcher`, `fetchCommand`, `pointersToFetchForRef`, `fetchRef`, `pointersToFetchForRefs`, `fetchRefs`, `fetchPreviousVersions`, `fetchRecent`, `fetchAll`, `scanAll`, `fetch`, `pointersToFetch`, and `getIncludeExcludeArgs`. It uses `lfs.GitScanner`, `tq.TransferQueue`, `tasklog`, `lfs.FetchPruneConfig`, and `newDownloadQueue`.

Control flow: parses remote and refs, supports stdin ref resolution, defaults to current ref unless `--all`, rejects incompatible flag combinations, builds path filters, scans requested refs or all history, optionally scans recent branches and previous versions, then downloads via a transfer queue. The watcher records transfers for JSON/dry-run and avoids duplicate observed OIDs under dry-run/refetch. `--prune` invokes shared prune after fetch.

State and persistence behavior: writes objects into local LFS storage, may link/copy from reference repositories before deciding a download is needed, and may prune local objects when requested. JSON output buffers observed transfers until the end; progress writes to stderr/stdout tasklog.

Dependencies/integration points: integrates Git ref resolution, recent branch discovery, commit summaries, filepath filters, transfer adapter manifests, API endpoints, prune configuration, and shared download queue construction.

Risks and test signals: risks include complex flag interactions, dry-run/refetch watcher state controlling duplicate suppression, `--all` ignoring configured filters, scanner multi-error accumulation, and prune after partial fetch. Test signals include stdin refs, explicit refs, current ref, `--all`, `--recent`, include/exclude, dry-run JSON, refetch existing objects, missing objects causing final failure, and fetch-prune behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_fetch.go -->
