# sources/object-store/minio-mc/cmd/event-list.go

Purpose: Implements `mc event list`/`ls` for bucket notifications.

Important APIs/types/functions: `eventListCmd`, `checkEventListSyntax`, `eventListMessage`, and `mainEventList`.

Control flow: Accepts target plus optional ARN, creates an S3 client, calls `ListNotificationConfigs`, and prints each returned config with events and filters.

State and persistence: Read-only against remote notification config.

Dependencies/integration: Uses S3 notification client methods, colorjson, console colors, and global context.

Risks: Usage text says `TARGET ARN` even though ARN is optional. String output always prints `Filter:` even when no filter is present.

Test signals: No direct tests.
