# sources/sync-backup/restic/cmd/restic/main.go

## Purpose

This file is the restic CLI entrypoint. It configures process-level runtime behavior, constructs the Cobra root command, registers all subcommands and global flags, applies feature flags, wires terminal status handling, normalizes command errors into user-facing messages, and maps errors to stable exit codes.

## Important APIs, Types, and Functions

- `init` calls `maxprocs.Set()` from `go.uber.org/automaxprocs/maxprocs` to honor container CPU limits while suppressing log output.
- `ErrOK` is a sentinel error used by commands to indicate a successful early exit that should override context cancellation.
- `cmdGroupDefault` and `cmdGroupAdvanced` identify Cobra command groups.
- `newRootCommand(globalOptions *global.Options)` constructs the root `*cobra.Command`, installs `PersistentPreRunE`, registers command groups, adds persistent global flags, disables Cobra's default completion command, registers every restic subcommand, and adds optional debug/mount/self-update/profiling hooks.
- `needsPassword(cmd string)` returns false for commands that should not invoke password retrieval (`cache`, `generate`, `help`, `options`, `self-update`, `version`, and Cobra completion commands).
- `tweakGoGC()` lowers default `GOGC` from 100 to 50 only when the user has not set a different value.
- `printExitError(globalOptions, code, message)` writes either a JSON `exit_error` object to stderr or a plain text message.
- `main()` performs runtime setup, command execution, error formatting, exit-code selection, and final `Exit(exitCode)`.

## Control Flow

Startup first adjusts garbage collection, redirects the standard logger to an in-memory buffer, and applies feature flags from `RESTIC_FEATURES`. It logs debug process/build information, constructs `global.Options` with all registered backends, then sets up terminal status around command execution. `newRootCommand(...).ExecuteContext(ctx)` runs Cobra. If the command returns nil, `main` checks the global context error; if it returns `ErrOK`, the error is cleared.

After command execution, `main` converts known error classes into messages: already locked errors include an unlock hint, invalid source data becomes a warning, fatal errors and missing keys receive special wording, and generic errors are formatted with stack/detail via `%+v`. If any library messages were captured in the log buffer, they are appended to the generic error message. A second switch maps errors to exit codes: success `0`, invalid source or failed snapshot removal `3`, no repository `10`, already locked `11`, no key `12`, context canceled `130`, and generic failure `1`.

## State and Persistence Behavior

The file affects process-wide state: Go GC percentage, logger output destination, enabled feature flags, terminal status setup, profiling registration, and process exit. It does not directly write repository data, but all command execution flows pass through the root command and `global.Options`. The in-memory log buffer is intentionally transient and only emitted on errors.

## Dependencies and Integration Points

Core dependencies are Cobra, automaxprocs, restic backend registry `internal/backend/all`, debug/logging, feature flags, global options, repository error predicates, and terminal status handling. It integrates every command constructor: backup, cache, cat, check, copy, diff, dump, features, find, forget, generate, init, key, list, ls, migrate, options, prune, rebuild-index, recover, repair, restore, rewrite, snapshots, stats, tag, unlock, and version. Optional debug, mount, self-update, and profiling registration are also attached here.

## Risks and Edge Cases

- Commands that do not need a password must be kept in sync with `needsPassword`; otherwise password commands may run unnecessarily or needed credentials may be skipped.
- Error-to-exit-code mapping is part of the CLI contract and affects scripts.
- Appending captured library logs to user-facing errors can expose noisy dependency logs, but only on generic errors.
- JSON output mode must encode errors cleanly; if JSON encoding itself fails, the code falls back to a plain diagnostic and debug log.
- Lowering GC can trade CPU for memory and is intentionally skipped if the user has set another `GOGC`.

## Test Signals

Command integration tests throughout `cmd/restic` exercise root command execution, pre-run behavior, lock errors, JSON output, and exit mappings indirectly. `integration_test.go` in this subset reaches `global.Options` command flows, repository opening, and error handling around backend behavior.
