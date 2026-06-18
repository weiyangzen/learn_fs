# sources/object-store/minio-mc/cmd/encrypt-main.go

Purpose: Registers the top-level `mc encrypt` command and its subcommands.

Important APIs/types/functions: `encryptSubcommands`, `encryptCmd`, and `mainEncrypt`.

Control flow: Wires `set`, `clear`, and `info` subcommands, applies global flags and setup, and routes missing/unknown subcommands through `commandNotFound`.

State and persistence: No direct state.

Dependencies/integration: Uses MinIO cli and shared command setup.

Risks: Dispatch-only file; behavior depends on subcommands and CLI framework.

Test signals: No direct tests.
