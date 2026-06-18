# sources/object-store/minio-mc/cmd/replicate-update.go

## Purpose
Implements `mc replicate update`/`edit`, modifying an existing server-side replication rule and optionally its associated remote target credentials, sync/proxy/path/healthcheck/bandwidth settings.

## Important APIs, types, and functions
- `replicateUpdateFlags` exposes rule fields (`--id`, `--tags`, `--storage-class`, `--state`, `--priority`, `--replicate`) and remote target fields (`--remote-bucket`, `--sync`, `--proxy`, `--bandwidth`, `--healthcheck-seconds`, `--path`).
- `checkReplicateUpdateSyntax` requires exactly one target.
- `modifyRemoteTarget` finds a target by ARN, validates bucket identity, parses replacement credentials/endpoint from `--remote-bucket`, and returns a cloned `madmin.BucketTarget` plus `madmin.TargetUpdateType` operations.
- `replicateUpdateMessage` formats success output.
- `mainReplicateUpdate` coordinates rule update and optional admin target update.

## Control flow
The main command validates arguments, loads the current replication config, requires `--id`, validates optional `--state`, extracts the source bucket from an `S3Client`, builds an admin client, and lists remote targets. It finds the ARN for the requested rule ID, preferring `rcfg.Role` when present.

If `--remote-bucket` is set, `modifyRemoteTarget` updates target credentials and any selected target attributes, then `UpdateRemoteTarget` persists the changes. If target-only flags are set without `--remote-bucket`, the command fails. It then parses `--replicate` into delete-marker, permanent-delete, metadata-sync, and existing-object replication statuses, builds `replication.Options`, and calls `client.SetReplication`.

## State and persistence
Persists remote server state only. `UpdateRemoteTarget` changes MinIO remote target configuration, while `SetReplication` changes bucket replication rules. No local config files are written.

## Dependencies and integration points
Uses MinIO client/admin constructors, `madmin.BucketTarget`, `madmin.TargetUpdateType`, `madmin.ParseARN`, `replication.Options`, `s3utils.CheckValidBucketName`, credential URL parsing, bandwidth parsing, and global fatal/print helpers.

## Risks and edge cases
- If the rule ID is not found, `arn` remains empty and `modifyRemoteTarget` will fail with not found; the replication options later also refer to that empty destination.
- Remote target updates validate target bucket and source bucket against the existing target to avoid accidental retargeting.
- `--sync`, `--proxy`, `--bandwidth`, `--healthcheck-seconds`, and `--path` are rejected unless `--remote-bucket` is also present.
- Credentials are parsed from URLs or aliases; malformed or missing bucket paths are fatal.
- `--replicate ""` intentionally disables all replicate subfeatures.

## Test signals
No direct tests in this subset. Good test coverage would exercise `modifyRemoteTarget` for ARN matching, credential URL parsing, sync/proxy validation, operation list construction, and `--replicate` parsing.
