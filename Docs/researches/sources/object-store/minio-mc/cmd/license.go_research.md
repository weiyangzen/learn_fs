# Research: sources/object-store/minio-mc/cmd/license.go

Purpose: registers the `mc license` command namespace.

Important APIs/types/functions: `licenseSubcommands`, `licenseCmd`, and `mainlicense`.

Control flow: dispatches register, info, update, and hidden unregister. Unknown subcommands go through `commandNotFound`.

State and persistence: none directly; subcommands manage SUBNET/local license state.

Dependencies/integration points: top-level CLI integration for license support commands.

Risks: hidden unregister remains part of command tree. Function name `mainlicense` is non-standard casing but local only.

Test signals: command-tree tests should verify visible and hidden command registration.
