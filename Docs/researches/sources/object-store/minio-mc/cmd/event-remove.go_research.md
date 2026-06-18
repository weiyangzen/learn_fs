# sources/object-store/minio-mc/cmd/event-remove.go

Purpose: Implements `mc event remove`/`rm` for deleting bucket notification configs.

Important APIs/types/functions: `eventRemoveFlags`, `eventRemoveCmd`, `checkEventRemoveSyntax`, `eventRemoveMessage`, and `mainEventRemove`.

Control flow: Requires target and optional ARN. If only target is supplied, `--force` is mandatory. It creates an S3 client, reads event/prefix/suffix filters, calls `RemoveNotificationConfig`, and prints success.

State and persistence: Mutates remote bucket notification configuration.

Dependencies/integration: Uses S3-specific notification APIs, global context, probe errors, and output helpers.

Risks: The `--force` guard protects remove-all behavior, but filtered removal with empty ARN depends on server method semantics. Event string is not split here, unlike add.

Test signals: No direct tests.
