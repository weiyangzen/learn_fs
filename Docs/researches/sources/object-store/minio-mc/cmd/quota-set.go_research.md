# Research: sources/object-store/minio-mc/cmd/quota-set.go

## sources/object-store/minio-mc/cmd/quota-set.go

Purpose: implements `mc quota set` and defines the shared quota output message type.

Important APIs and types: `quotaSetCmd`, `quotaMessage`, `checkQuotaSetSyntax`, and `mainQuotaSet`. `quotaMessage.String` formats set, clear, and info variants; `JSON` emits structured output.

Control flow: syntax requires one target and `--size`. The handler parses size with `humanize.ParseBytes`, uses `madmin.HardQuota`, constructs an admin client, calls `SetBucketQuota`, and prints success.

State and persistence: mutates remote bucket quota state to a hard quota. No local state changes.

Dependencies and integration: uses `madmin.BucketQuota`, humanize byte parsing, colorized console themes, shared output, and sibling quota commands for message reuse.

Risks and tests: only hard quotas are supported by this CLI path. Size zero is not explicitly rejected. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/quota-set.go -->
