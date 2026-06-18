# sources/sync-backup/restic/cmd/restic/cmd_copy.go

Purpose: implements `restic copy`, copying snapshots and referenced blobs from one repository to another, re-encrypting data for the destination repository.

Important APIs/types/functions: `CopyOptions` embeds `SecondaryRepoOptions` and snapshot filters. `collectAllSnapshots` filters source snapshots and skips already-copied equivalents based on `Original` IDs and `similarSnapshots`. `runCopy` opens source/destination repos and loads indexes. `copyTreeBatched`, `copyTree`, `copyStats`, and `copySaveSnapshot` copy referenced tree/data blobs and save copied snapshot metadata.

Control flow: resolves whether secondary options represent source or destination, opens source read lock and destination append lock, memorizes snapshot lists, loads both indexes, builds a destination map by original/current IDs, iterates source snapshots, copies missing blobs in batches through destination blob uploader, then saves snapshots with parent cleared and original ID preserved.

State/persistence: writes data/tree blobs, pack files, indexes, and snapshot files to the destination repository. Source repository is read-only. Destination snapshots get new IDs and retain source identity in `Original`.

Dependencies/integration: repository copy helpers, data snapshot filtering, blob indexes, progress UI, and secondary repo global options.

Risks/test signals: deduplication is limited by chunker compatibility and existing destination blobs. Snapshot equivalence ignores parent/original. Tests cover full copy integrity, incremental copy skipping, unstable JSON/symlink data, reverse copy, and empty-password destination.
