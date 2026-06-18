<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top.go -->
# sources/object-store/minio-mc/cmd/support-top.go

Purpose: defines the `mc support top` command namespace for real-time MinIO operational views.

Important APIs/types/functions: `supportTopSubcommands`, `supportTopCmd`, and `mainSupportTop`.

Control flow: registers `api`, `drive`, `locks`, `net`, and `rpc` subcommands. If invoked without a known subcommand, `mainSupportTop` delegates to `commandNotFound`.

State and persistence: no state changes in this file; streaming/read-only behavior is implemented in subcommand files.

Dependencies and integration points: integrated under top-level `support` command and the MinIO CLI package.

Risks and test signals: low logic risk; command availability and help behavior are the main concerns. Tests should verify subcommand registration and invalid-subcommand handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top.go -->
