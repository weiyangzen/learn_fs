<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_restore.go -->
# sources/sync-backup/kopia/cli/command_restore.go

Purpose: implements `kopia restore`, restoring snapshot/object contents to local filesystem or archive outputs, and expanding shallow placeholder files in place.

Important APIs/types/functions: `commandRestore`, `restoreSourceTarget`, `RestoreProgress`, `constructTargetPairs`, `restoreOutput`, `detectRestoreMode`, `setupPlaceholderExpansion`, `run`, `tryToConvertPathToID`, `createSnapshotTimeFilter`, `computeMaxTime`, `findLastManifestWithPath`, `restore.Entry`, and `snapshotfs`.

Control flow: setup registers source args and restore flags for overwrite, sparse files, attributes, mode, parallelism, skip metadata, incremental/delete-extra, shallow placeholders, snapshot time, and flushing. `run` builds an output, resolves each source either from placeholders or object IDs/paths, obtains a root filesystem entry, invokes `restore.Entry` with progress callback and options, flushes progress, and logs stats.

State/persistence behavior: writes restored files/directories/symlinks, zip/tar/tgz archives, or placeholder expansions on local disk. Repository is read-only. Path-source restore resolves latest/oldest/time-bounded complete snapshot manifests before restoring.

Dependencies/integration: integrates localfs, snapshot manifests, object IDs, restore outputs, progress UI, archive writers, time parsing, and policy-independent snapshotfs lookup. Risks/test signals: restore can overwrite/delete local files depending on flags; archive outputs are created with `os.Create`, truncating existing target files.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_restore.go -->
