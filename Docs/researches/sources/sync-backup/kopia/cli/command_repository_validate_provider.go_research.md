<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_validate_provider.go -->
# sources/sync-backup/kopia/cli/command_repository_validate_provider.go

Purpose: implements `repository validate-provider`, running blob storage validation against the connected direct repository storage.

Important APIs/types/functions: `commandRepositoryValidateProvider`, `blobtesting.Options`, `blobtesting.Verify`, `repo.DirectRepositoryWriter`, and `dr.BlobStorage()`.

Control flow: setup registers the command with the advanced direct repository write action and exposes validation flags from `blobtesting.Options`. `run` passes the direct repository's blob storage to `blobtesting.Verify`.

State/persistence behavior: validation may write, read, list, and delete test blobs in repository storage according to blobtesting behavior. It does not change repository format metadata intentionally.

Dependencies/integration: depends on direct storage access, provider capabilities, and blobtesting validation logic. Risks/test signals: intended after repository creation to verify provider compatibility; running against production storage still performs live storage operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_validate_provider.go -->
