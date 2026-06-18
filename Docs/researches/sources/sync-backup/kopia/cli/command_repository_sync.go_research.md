<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_sync.go -->
# sources/sync-backup/kopia/cli/command_repository_sync.go

Purpose: implements `repository sync-to`, copying raw repository blobs from the currently connected direct repository to another storage provider, optionally updating newer blobs, deleting extras, and preserving timestamps.

Important APIs/types/functions: `commandRepositorySyncTo`, `runSyncWithStorage`, `listDestinationBlobs`, `runSyncBlobs`, `sliceToChannel`, `syncCopyBlob`, `syncDeleteBlob`, `ensureRepositoriesHaveSameFormatBlob`, `parseUniqueID`, `errgroup`, `gather.WriteBuffer`, and `blob.Storage`.

Control flow: setup registers sync flags and provider subcommands. The run path opens the source as a direct repository, verifies destination format blob is missing or has the same unique ID, lists destination metadata, lists source blobs to compute copy/update/in-sync sets, optionally builds delete set, exits on dry-run, then parallel workers copy blobs first and delete extra blobs second.

State/persistence behavior: writes the destination repository format blob when absent unless `--must-exist` is set, copies blob bytes, optionally sets modification times, and deletes destination-only blobs only with `--delete`.

Dependencies/integration: raw blob storage APIs, progress reporting, format JSON parsing, and direct repository access. Risks/test signals: sync is storage-level replication; incompatible unique IDs are blocked, but concurrent source mutation can still race with blob listing/copying.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_sync.go -->
