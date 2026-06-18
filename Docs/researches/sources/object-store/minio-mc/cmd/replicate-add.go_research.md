# Research: sources/object-store/minio-mc/cmd/replicate-add.go

## sources/object-store/minio-mc/cmd/replicate-add.go

Purpose: implements `mc replicate add`, configuring a remote replication target and adding a bucket replication rule.

Important APIs and types: `replicateAddCmd`, `replicateAddMessage`, `extractCredentialURL`, `fetchRemoteTarget`, `getBandwidthInBytes`, and `mainReplicateAdd`.

Control flow: syntax requires one source target and `--remote-bucket`. Remote credentials are extracted either from URL userinfo-like forms or existing aliases; temporary tokens are rejected. `fetchRemoteTarget` validates path style, target bucket, bandwidth, proxy, sync, region, and health interval into `madmin.BucketTarget`. The handler ensures the source is S3, registers the remote target through admin API, fetches existing replication config, translates `--replicate` options into replication flags, and calls `SetReplication(AddOption)`.

State and persistence: mutates remote target configuration and bucket replication XML/configuration on the source bucket.

Dependencies and integration: uses `madmin`, MinIO replication package, alias config, credential regexes, S3 bucket validation, and shared CLI output.

Risks and tests: credentials embedded in CLI arguments are parsed and then stored in remote target config. Priority is required by help but not explicitly checked for nonzero here. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-add.go -->
