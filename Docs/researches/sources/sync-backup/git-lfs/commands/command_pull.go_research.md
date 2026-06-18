<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_pull.go -->
# sources/sync-backup/git-lfs/commands/command_pull.go

Purpose: implements `git lfs pull`, downloading LFS objects for the current ref and checking them out into the working tree.

Important APIs/types/functions: `pullCommand`, `pull`, `pointerMap`, `newPointerMap`, `Seen`, `Add`, and `All`; `lfs.GitScanner.ScanLFSFiles`, `newSingleCheckout`, `newDownloadQueue`, and `tq.Meter`.

Control flow: validates Git version/repository, optionally sets remote, builds include/exclude filter, scans current ref for LFS pointers, immediately checks out objects already present locally, queues missing unique OIDs for download while mapping all paths to each OID, watches download completion to checkout all paths for that OID, waits for scan/queue/watch completion, reports transfer errors, and warns if checkout was skipped because LFS is not installed.

State and persistence behavior: downloads media into local LFS storage and mutates working-tree files. `pointerMap` holds in-memory OID-to-path associations and deletes them after checkout.

Dependencies/integration points: integrates current ref resolution, reference object linking, transfer queue progress, single checkout, filepath filters, remote endpoint failure reporting, and clone command reuse.

Risks and test signals: risks include callback and watcher concurrency, duplicate OID mapping correctness, checkout of already-present objects before meter start, and partial download failure after some checkouts. Test signals include current ref pull, include/exclude, duplicate OID multiple paths, existing object checkout, missing object download/checkout, transfer errors, and skip checkout when hooks/filter missing.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_pull.go -->
