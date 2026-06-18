<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmd.go -->
# sources/user-network-fs/rclone/cmd/cmd.go

## Purpose

`cmd.go` is the central command runtime for rclone. It provides version printing, filesystem argument resolution, root command execution, retries, stats/progress lifecycle, global config initialization, backend flag registration, and exit-code mapping.

## Important APIs, Types, and Functions

Key helpers are `ShowVersion`, `NewFsFile`, `NewFsSrc`, `NewFsDir`, `NewFsSrcDst`, `NewFsSrcFileDst`, `NewFsSrcDstFiles`, and `NewFsDstFile`. `Run` wraps command work with retry accounting, stats/progress, signal handling, cache shutdown, dumps, and final exit resolution. `CheckArgs` performs fatal usage validation. `StartStats` owns a periodic stats goroutine. `initConfig` initializes global options, logging, config file loading, accounting, console behavior, rc/metrics servers, and CPU/memory profiling. `resolveExitCode`, `AddBackendFlags`, and `Main` finish process behavior.

## Control Flow

`Main` configures the root command, adds backend flags, and executes Cobra. Each command typically validates args, constructs Fs values through these helpers, and calls `Run`. `Run` invokes the command function repeatedly until success, fatal/no-retry status, retry exhaustion, or disabled retries, then exits the process.

## State and Persistence Behavior

The file pins CLI Fs cache entries, clears cache on completion, mutates global config/accounting/logging state, starts rc/metrics servers, can create profile files, and always exits via `os.Exit`.

## Dependencies and Integration Points

It ties together `fs`, `cache`, `filter`, `accounting`, `configfile`, `configflags`, `rcserver`, `sync` errors, terminal handling, atexit callbacks, build info, Cobra, and pflag.

## Risks and Test Signals

Risks include process-exit behavior in tests, global state leakage, retrying side-effecting operations, filter conflicts with single-file sources, incorrect destination file/dir inference, goroutine leaks in stats/progress, and exit-code regressions. Tests should isolate exit behavior, cover Fs helper edge cases, retry classification, profile setup errors, `--error-on-no-transfer`, backend flag generation, and cache cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmd.go -->
