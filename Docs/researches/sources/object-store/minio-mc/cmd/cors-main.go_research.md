# sources/object-store/minio-mc/cmd/cors-main.go

Purpose: Registers the top-level `mc cors` command and subcommands.

Important APIs/types/functions: `corsSubcommands`, `corsCmd`, and `mainCors`.

Control flow: The command wires `set`, `get`, and `remove` subcommands, applies `setGlobalsFromContext` and global flags, and delegates unknown invocations to `commandNotFound`.

State and persistence: No state or persistence.

Dependencies/integration: Integrates with the global CLI command tree through `github.com/minio/cli` and shared global flag handling.

Risks: Behavior is only dispatch. Missing subcommand help/usage depends on `commandNotFound` implementation outside this subset.

Test signals: No direct tests.
