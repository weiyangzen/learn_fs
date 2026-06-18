# sources/object-store/minio-mc/cmd/event-main.go

Purpose: Registers the top-level `mc event` command and subcommands.

Important APIs/types/functions: `eventFlags`, `eventSubcommands`, `eventCmd`, and `mainEvent`.

Control flow: Wires `add`, `remove`, and `list`, applies global flags, hides help command, and handles missing subcommands through `commandNotFound`.

State and persistence: None directly.

Dependencies/integration: MinIO cli command tree and global setup.

Risks: Dispatch-only; all behavior resides in subcommands.

Test signals: No direct tests.
