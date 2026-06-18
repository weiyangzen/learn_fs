# sources/sync-backup/kopia/repo/buildinfo.go

Purpose: initializes user-visible build metadata and version from linker-provided values or Go module build information.

Important APIs/types/functions: global variables are `BuildInfo`, `BuildVersion`, and `BuildGitHubRepo`. `init` calls `getBuildInfoAndVersion`; `getRevisionString` formats VCS settings into `time-revision(+dirty)`.

Control flow: if both linked info and version are set, they win. Otherwise `debug.ReadBuildInfo` is queried. Missing version defaults to `v0-unofficial` unless module version is nonempty and not `(devel)`. Missing info becomes the revision string built from `vcs.revision`, `vcs.time`, and `vcs.modified`.

State and persistence behavior: process-global variables are set at init time only. No files are read or written.

Dependencies/integration: consumed by CLI/about/version reporting and packaging. Uses standard `runtime/debug` and falls back to stdlib logging before Kopia logging is configured.

Risks and edge cases: missing VCS settings produce `-(unknown_revision)`. Dirty detection is case-insensitive only for value `true`. Go toolchain behavior around `(devel)` is explicitly handled.

Test signals: `buildinfo_test.go` validates revision string combinations for missing revision, VCS time, revision, and dirty state.
