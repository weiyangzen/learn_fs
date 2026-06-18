# sources/user-network-fs/rclone/cmd/bisync/cmd.go

Purpose: Defines the `rclone bisync` CLI command, command flags, option structure, check-sync enum, and option pre-processing for filters, dry-run, workdir, and max-delete behavior.

Important APIs/types/functions: `Options` is the central user-facing configuration consumed by `Bisync`. `CheckSyncMode` supports `true`, `false`, and `only` with `String`, `Set`, and `Type` for flag/RC parsing. Global `Opt` backs cobra flags. `commandDefinition` validates two directory arguments and calls `Bisync`. `Options.applyContext`, `setDryRun`, and `applyFilters` bridge global fs config into bisync-specific options.

Control flow: Package init registers the command, binds all bisync flags, hides debugging flags, and registers the RC endpoint. CLI execution rejects file arguments, copies global `Opt`, applies context-derived defaults, optionally sets listing timezone to local, warns for Dropbox/no common hash/refresh-times, then runs `Bisync` under `cmd.Run`. `applyFilters` validates an external filters file by MD5 sidecar: non-resync runs require an unchanged `.md5`; resync writes or logs the hash depending on dry-run.

State and persistence behavior: `DefaultWorkdir` is under rclone's cache dir. Filter integrity is persisted in `<filters-file>.md5`; changing filters without `--resync` aborts. `applyContext` copies `ci.MaxDelete` into bisync's option and resets the global value to `-1` so lower-level operations do not enforce a separate max-delete policy. `setDryRun` creates a context with `ci.DryRun` set from bisync options.

Dependencies and integration points: Integrates with rclone `cmd`, cobra, flag helpers, fs config, filters, hashes, `bilib`, and `fserrors.FatalError` for aborted runs. Flag comments explicitly require keeping `rc.go`, `help.go`, and user docs synchronized.

Risks: The global `Opt` and `tzLocal` are package state and must be copied before mutation. New flags can drift from RC/help generation if not updated. Filter hash enforcement depends on users preserving the `.md5` sidecar. The Dropbox refresh-times warning is heuristic and name-prefix based.

Test signals: CLI parsing is indirectly covered by scenario flags in `bisync_test.go`; RC parity is covered through generated help and `rcBisync` option mapping. Direct unit tests should cover `CheckSyncMode.Set`, max-delete clamping, filter hash mismatch/resync behavior, and directory-only argument rejection.
