# Research: sources/object-store/minio-mc/cmd/quota-info.go

## sources/object-store/minio-mc/cmd/quota-info.go

Purpose: implements `mc quota info`, displaying current bucket quota configuration.

Important APIs and functions: `quotaInfoCmd`, `checkQuotaInfoSyntax`, and `mainQuotaInfo`.

Control flow: syntax requires exactly one target. The handler creates an admin client, derives target bucket, calls `GetBucketQuota`, chooses `qCfg.Size` when nonzero otherwise `qCfg.Quota`, and prints a `quotaMessage` with quota type and size.

State and persistence: read-only remote operation; no persistent mutation.

Dependencies and integration: uses `madmin` quota APIs, shared `quotaMessage`, `probe.NewError`, and command/global output flags.

Risks and tests: legacy fields `Quota` and `Size` are reconciled by preference but edge cases with both set are implicit. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/quota-info.go -->
