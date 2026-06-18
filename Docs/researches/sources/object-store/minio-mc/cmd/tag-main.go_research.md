<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-main.go -->
# sources/object-store/minio-mc/cmd/tag-main.go

Purpose: defines the `mc tag` command namespace.

Important APIs/types/functions: `tagSubcommands`, `tagCmd`, and `mainTag`.

Control flow: registers `list`, `remove`, and `set` as subcommands. Unknown or missing subcommands are handled through `commandNotFound`.

State and persistence: no state changes here; subcommands read or mutate tags.

Dependencies and integration points: integrated into the main command tree and uses the MinIO CLI framework plus global flags.

Risks and test signals: low risk. Tests should verify command registration, help text, and invalid-subcommand behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-main.go -->
