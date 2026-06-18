# sources/object-store/minio-mc/cmd/event-add.go

Purpose: Implements `mc event add` to add bucket notification targets.

Important APIs/types/functions: `eventAddFlags`, `eventAddCmd`, `checkEventAddSyntax`, `eventAddMessage`, and `mainEventAdd`.

Control flow: Requires target and ARN, parses event list plus prefix/suffix and ignore-existing flag, creates a client, requires it to be `S3Client`, calls `AddNotificationConfig`, and prints success.

State and persistence: Mutates remote bucket notification configuration.

Dependencies/integration: Uses S3-specific notification methods, CLI flags, global context, colorjson, and console output.

Risks: Event string is split without trimming/validation here. Non-S3 targets are rejected at runtime.

Test signals: No direct tests.
