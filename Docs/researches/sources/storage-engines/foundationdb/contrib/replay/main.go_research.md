# sources/storage-engines/foundationdb/contrib/replay/main.go

## Purpose

`main.go` is the CLI entrypoint for the Go `replay` TUI. It selects a trace XML file, parses it into `TraceData`, reports load summary details, and launches the interactive UI.

## Important APIs and Functions

- `main()` calls `run()`, writes errors to stderr, and exits with code 1 on failure.
- `run()` handles arguments, trace discovery, parsing, summary logging, and `runUI(traceData)`.
- `printHelp()` writes usage, examples, and interaction hint text to stderr.
- `findLatestTraceFile()` finds the most recently modified `trace*.xml` file in the current working directory.

## Control Flow

`run()` accepts exactly three modes:

- One argument `-h` or `--help`: print help and return success.
- One non-help argument: treat it as the explicit trace file path.
- No arguments: call `findLatestTraceFile()` and use the newest matching file in the current directory.

Any other argument count returns a usage error. Once a trace path is chosen, `run()` calls `parseTraceFile()`. Parse errors are wrapped with context. On success it logs event count, min/max time, configuration count, and recovery state count, then calls `runUI(traceData)`.

`findLatestTraceFile()` uses `filepath.Glob("trace*.xml")`, stats each match, skips stat failures, and returns the path with the latest modification time.

## State and Persistence Behavior

The CLI keeps no persistent state. It reads from the current directory when auto-detecting traces and relies on `parseTraceFile()` to load trace contents into memory. Process exit code communicates failure to shell users.

## Dependencies and Integration Points

This file depends on standard packages `fmt`, `os`, `path/filepath`, and `time`. It integrates with `trace.go` via `parseTraceFile()` and with `ui.go` via `runUI()`. The CMake file builds this package into the `replay` binary.

## Risks and Edge Cases

- Auto-discovery only searches the current working directory and only the `trace*.xml` pattern.
- `printHelp()` writes to stderr even on successful help, which may surprise scripts expecting help on stdout.
- A single argument that begins with `-` but is not help is treated as a file path, not an unknown option.
- `findLatestTraceFile()` breaks ties by first encountered glob order because it only updates on strictly newer modification time.
- File existence for an explicit trace path is not checked until `parseTraceFile()`.

## Test Signals

Tests should cover help mode, explicit path mode, no-argument latest-file discovery, no matches, inaccessible matches, too many arguments, parse failure propagation, and successful handoff to a replaceable/testable UI entrypoint if refactoring makes `runUI` injectable.
