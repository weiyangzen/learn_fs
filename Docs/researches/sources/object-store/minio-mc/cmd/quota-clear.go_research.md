# Research: sources/object-store/minio-mc/cmd/quota-clear.go

## sources/object-store/minio-mc/cmd/quota-clear.go

Purpose: implements `mc quota clear`, removing bucket quota configuration.

Important APIs and functions: `quotaClearCmd`, `checkQuotaClearSyntax`, and `mainQuotaClear`.

Control flow: syntax requires exactly one target. The handler sets colors, creates an admin client for the target alias, derives the bucket path with `url2Alias`, calls `SetBucketQuota` with an empty `madmin.BucketQuota`, and prints a `quotaMessage`.

State and persistence: mutates remote bucket quota state by clearing it. No local storage mutation.

Dependencies and integration: uses `madmin.AdminClient`, `quotaMessage` from `quota-set.go`, shared output and fatal handling.

Risks and tests: bucket name extraction uses `url2Alias(args[0])` and assumes the path is a bucket suitable for quota APIs. There are no direct quota tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/quota-clear.go -->
