<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_upload.go -->
# sources/sync-backup/kopia/cli/command_policy_set_upload.go

Purpose: implements upload concurrency policy flags for file reads, server/UI snapshot parallelism, and threshold for parallel upload.

Important APIs/types/functions: `policyUploadFlags`, `setUploadPolicyFromFlags`, `applyOptionalInt`, `applyOptionalInt64MiB`, and `policy.UploadPolicy`.

Control flow: setup registers `--max-parallel-file-reads`, `--max-parallel-snapshots`, and `--parallel-upload-above-size-mib`. The setter applies optional integer parsing to the first two and parses the threshold as MiB, converting to bytes.

State/persistence behavior: stores optional integer pointers in upload policy. Nil means inherited/default. The threshold conversion persists bytes even though the CLI accepts MiB.

Dependencies/integration: consumed by snapshot upload workers and server/UI scheduling paths. Risks/test signals: parser accepts raw integers only; negative values are not rejected in this layer unless lower policy validation rejects them elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_upload.go -->
