# sources/storage-engines/foundationdb/packaging/docker/fdb-aws-s3-credentials-fetcher/fdb-aws-s3-credentials-fetcher.go

Purpose: This Go sidecar continuously writes FoundationDB blob-storage S3 credential JSON from AWS SDK credentials. It is intended for EKS/IRSA or other AWS credential sources so FDB processes can authenticate to S3.

Important APIs and types: `BlobCredentials` contains account mappings to `Account` records with `secret`, `api_key`, and `token`. `writeCredentialsFile` writes `s3_blob_credentials.json`; `refreshCredentials` loads AWS default config and retrieves credentials; `main` parses pflag options including `--region`, `--dir`, `--bucket`, `--run-once`, and `--expiry-threshold`.

Control flow: The program validates `--dir`, creates it, computes the credential file path, optionally refreshes once and exits, or starts a 5-minute ticker loop. Each refresh loads AWS config for the region, retrieves credentials, and writes account entries for regional S3 host, `:443`, bucket regional host, and bucket `:443`.

State and persistence behavior: Persistent state is the JSON credential file under the configured directory, mode `0644`. It rewrites credentials each interval rather than comparing expiry. No in-memory secret cache survives process exit.

Dependencies and integration points: It uses AWS SDK v2 config loading, `spf13/pflag`, Kubernetes/EKS credential providers via the default chain, and FoundationDB blob credential file conventions.

Risks: `expiryThreshold` is parsed but not used in refresh decisions. The default bucket contains a specific account-like name, which may not fit other deployments. File mode `0644` exposes credentials to same-container users. Tests should validate JSON shape, host-key variants, run-once behavior, AWS config failures, region/bucket overrides, and credential file permissions.
