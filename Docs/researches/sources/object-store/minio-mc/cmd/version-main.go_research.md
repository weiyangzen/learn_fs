## sources/object-store/minio-mc/cmd/version-main.go

Purpose: registers the top-level `mc version` command and its `enable`, `suspend`, and `info` subcommands. Important symbols are `versionSubcommands`, `versionCmd`, and `mainVersion`.

Control flow delegates all real behavior to subcommands; invoking `mc version` without a valid subcommand calls `commandNotFound`. State and persistence are absent. Dependencies are the local subcommand variables and `github.com/minio/cli`. Integration is purely CLI routing with global flags and `setGlobalsFromContext`. Risks are minimal but include forgetting to add new subcommands to `versionSubcommands`, which would make them unreachable. Test signal is indirect through CLI command table tests, not present in this subset.
