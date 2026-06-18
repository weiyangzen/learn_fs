# sources/user-network-fs/rclone/cmd/bisync/rc.go

Purpose: Registers and implements the `sync/bisync` remote-control endpoint, including embedded help text, option parsing from `rc.Params`, execution, captured output, and returned workdir/listing metadata.

Important APIs/types/functions: `addRC` registers the call. `rcHelp` embeds generated `rc.md`. `shortHelp`, `longHelp`, and `MakeHelp` provide shared command/help text. `rcBisync` parses RC parameters and calls `Bisync`. `setEnum` parses optional enum strings with defaults.

Control flow: `rcBisync` creates a derived config context, reads optional booleans, strings, ints, durations, and enum values using camelCase parameter names, validates `maxDelete`, supports backward-compatible `backupdir1/backupdir2`, resolves `path1` and `path2` with `rc.GetFsNamed`, captures bisync output, writes it to the configured rclone log writer, computes canonical workdir/basePath, and returns output/session/workdir/listing/log metadata.

State and persistence behavior: The endpoint itself persists no state beyond whatever `Bisync` writes into the selected workdir. It returns exact listing paths so RC callers can inspect persisted state. It mutates only the derived config context for dry-run and other options.

Dependencies and integration points: Integrates with rclone `fs/rc`, `fs/log`, `bilib.BasePath`, `bilib.CaptureOutput`, command help generation, and the same `Options` structure used by CLI. `cmd.go` init calls `addRC`.

Risks: CLI and RC option parity is manual except for generated docs; adding a new option requires updating this parser. Optional-parameter logging uses `rc.NotErrParamNotFound` patterns that are easy to invert if edited carelessly. Captured output can be large for verbose runs. Defaults for enums depend on zero-value `Options` string methods.

Test signals: RC-specific tests should call `sync/bisync` with minimal params, invalid maxDelete, enum params, dryRun, custom workdir, and backward-compatible backupdir casing. Existing integration tests mainly exercise the package API, not RC.
