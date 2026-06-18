<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy.go -->
# sources/object-store/minio-mc/cmd/support-proxy.go

Purpose: defines the `mc support proxy` command namespace and wires its subcommands.

Important APIs/types/functions: `supportProxySubcommands`, `supportProxyCmd`, and `mainSupportProxy`.

Control flow: the command registers `set`, `remove`, and `show` subcommands with support/global flags. If invoked without a valid subcommand, `mainSupportProxy` delegates to `commandNotFound`.

State and persistence: no state changes in this file; stateful behavior lives in subcommand files.

Dependencies and integration points: integrates with the top-level `supportSubcommands` list in `support.go` and uses the MinIO CLI framework.

Risks and test signals: low logic risk, but command registration is user-facing. Tests should confirm the subcommand list is reachable, help text is correct, and invalid subcommands produce standard command-not-found behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy.go -->
