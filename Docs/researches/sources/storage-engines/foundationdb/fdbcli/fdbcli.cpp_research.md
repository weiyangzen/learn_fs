# sources/storage-engines/foundationdb/fdbcli/fdbcli.cpp

## Purpose

`fdbcli.cpp` is the FoundationDB CLI executable. It parses process options, initializes the client API and network, constructs the interactive shell, parses user command lines, dispatches built-in and command-factory commands, manages transaction state, and handles status checks, history, completion, hints, TLS diagnostics, logging, memory limit monitoring, and `--exec` mode.

## Important APIs, Types, and Functions

- `CLIOptions` parses command-line flags with `SimpleOpt`, including cluster file, API version, trace options, TLS options, `--exec`, timeout, status-from-json, knobs, and memory limit.
- `FdbOptions` stores persistent transaction options and applies them to new or active transactions.
- `parseLine` tokenizes semicolon-separated CLI commands with quotes and escape sequences.
- `formatStringRef`, `printProgramUsage`, `initHelp`, `printHelpOverview`, `printHelp`, `printVersion`, and `printBuildInformation` provide display behavior.
- `makeInterruptable`, `commitTransaction`, `checkStatus`, `timeWarning`, and `getTransaction` coordinate Flow futures and transaction lifecycle.
- Completion and hints are implemented by `fdbcliCompCmd`, `arrayGenerator`, and `LineNoise::Hint` logic in `runCli`.
- `cli` is the central async REPL and dispatcher.
- `main` performs platform setup, signal handling, network options, cluster-file resolution, TLS consistency checks, API setup, and network execution.

## Control Flow

`main` initializes platform/error state, ignores SIGINT on Unix, parses `CLIOptions`, sets tracing/TLS/network options, handles early-exit modes, resolves the cluster file, verifies TLS configuration against coordinator addresses, selects the API version, starts network setup, and runs `runCli` through `stopNetworkAfter`. `runCli` constructs `LineNoise`, loads history, calls `cli`, and saves history on exit.

`cli` creates both `Database` and multiversion `IDatabase` handles, performs an initial read-version handshake, optionally prints status and welcome text, then loops over either `--exec` content or interactive input. Each line is parsed into one or more commands. Parse failures insert a synthetic `parse_error` command so partial malformed commands are not executed. For each command it validates known commands against `helpMap` and `hiddenCommands`, handles built-ins directly, dispatches command actors, updates `is_error`, and stops remaining semicolon-separated commands after a failure. In interactive mode it maintains command history and long-delay status warnings; in exec mode it exits with status 1 on command failure.

## State and Persistence Behavior

Persistent database mutation is done by dispatched commands or by built-ins gated by `writemode`: `set`, `clear`, and `clearrange`. The CLI keeps local state for `intrans`, `writeMode`, active/global transaction options, cached worker/storage interface maps, current transaction reference, warning future, and line history. Explicit `begin` switches to an active transaction and copies global options; `commit`, `rollback`, and exception handling leave transaction mode. Autocommit writes call `commitTransaction` immediately.

## Dependencies and Integration Points

This file is the integration point for most `fdbcli` command actors declared in `fdbcli.h`, plus `LineNoise`, `MultiVersionApi`, `DatabaseContext`, status JSON, global config, management API, TLS config, cluster connection files, knobs, and Flow runtime. It also exposes `arrayGenerator` used by command-specific completion code.

## Risks and Edge Cases

`parseLine` mutates the input string while preserving `StringRef` slices; its erase/replace behavior is delicate and explicitly suppresses a clang-tidy false positive. Exact CLI output is test-sensitive. Long dispatch chains make it easy for new commands to be registered in help but omitted from dispatch or vice versa. `--timeout` races `cliFuture` with `timeExit`; when the timeout wins, `main` returns 1. Some interactive-only paths, such as unlock passphrase prompting and history filtering, require subprocess tests. `getrange` limit parsing manually caps at nine digits and accepts only decimal digits.

## Test Signals

`fdbcli_tests.py` covers much of this file indirectly: `--exec`, exact output, transactions, `writemode`, options, `clearrange` prefix mode, `status --json`, `--status-from-json`, TLS coordinator suffix rejection, command sequencing, lock/unlock prompts, and dispatch for many command actors. Parser edge cases for quoting and escapes are mostly implicit and would benefit from focused tests.
