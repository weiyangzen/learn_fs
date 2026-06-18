<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_repair.go -->
# sources/sync-backup/kopia/cli/command_repository_repair.go

Purpose: hidden deprecated repair command for recovering the `kopia.repository` format blob from older-format pack replicas.

Important APIs/types/functions: `commandRepositoryRepair`, `packBlockPrefixes`, `runRepairCommandWithStorage`, `recoverFormatBlob`, `format.RecoverFormatBlob`, `format.KopiaRepositoryBlobID`, `content.PackBlobIDPrefixes`, and `blob.Storage`.

Control flow: setup registers hidden provider subcommands and dangerous-command gating. The run path optionally checks whether the format blob already exists in `auto`, resolves search prefixes, lists blobs under those prefixes, attempts recovery from each blob, and writes the recovered bytes back as the repository format blob unless dry-run is set.

State/persistence behavior: can create the format blob in repository storage. Dry-run performs discovery without writing. It never modifies pack blobs.

Dependencies/integration: depends on low-level blob storage access and legacy format replicas. Risks/test signals: intentionally dangerous and hidden; a false positive recovery or wrong storage target could write an invalid format blob.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_repair.go -->
