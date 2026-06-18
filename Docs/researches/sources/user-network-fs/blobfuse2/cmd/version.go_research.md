# sources/user-network-fs/blobfuse2/cmd/version.go
## sources/user-network-fs/blobfuse2/cmd/version.go

Purpose: implements `blobfuse2 version`, printing the current version and optionally checking remote release metadata.

Important APIs/functions: global `check` flag and `versionCmd`. `init` registers the command under `rootCmd` and adds `--check`.

Control flow: when executed, the command prints `blobfuse2 version: <common.Blobfuse2Version>`. If `--check` was supplied, it calls `VersionCheck()` from `root.go`; otherwise it returns nil.

State and persistence: reads the global version string and global `check` flag. It writes to stdout and may perform network I/O through `VersionCheck`. No files are changed.

Dependencies/integration: Cobra command tree, `common.Blobfuse2Version`, and root version-check helpers. The command participates in `parseArgs` handling from `root.go`, including normal CLI use and `--version`.

Risks: the global `check` variable is process state, so tests or repeated command execution must reset flags. With `--check`, command latency and success depend on the remote sentinel files and network availability.

Test signals: `root_test.go` includes parse-args cases for `version` and `version --check=true`; direct execution of `versionCmd` is not separately asserted in this subset.
