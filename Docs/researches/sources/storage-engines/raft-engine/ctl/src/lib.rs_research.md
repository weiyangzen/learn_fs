# sources/storage-engines/raft-engine/ctl/src/lib.rs

## Purpose
Implements the reusable control-command library behind `raft-engine-ctl`, exposing typed command-line parsing and execution over an injectable filesystem.

## Important APIs, Types, And Functions
`ControlOpt` is the Clap parser. `Cmd` variants are `Dump`, `Check`, `Repair`, and `TryPurge`. `convert_queue` maps CLI strings to `LogQueue`. `ControlOpt::validate_and_execute`, `validate_and_execute_with_file_system`, and `run_command` are the execution entry points.

## Control Flow
Execution rejects missing subcommands. `Dump` creates a `LogItemReader` via `Engine::dump_with_file_system` and prints each decoded item, optionally filtering by raft group IDs. `Repair` reads a Rhai script file and invokes `Engine::unsafe_repair_with_file_system` over append, rewrite, or all queues. `Check` runs consistency checking and prints corrupted raft groups with last intact indexes. `TryPurge` opens an engine on the target path and prints the result of `purge_expired_files`.

## State And Persistence Behavior
Dump and check are read-only. Repair can rewrite data files according to a script and is intentionally named unsafe. Try-purge opens the engine and may rewrite/purge expired files, changing log file layout while preserving logical engine state.

## Dependencies And Integration Points
Depends on Clap, `DefaultFileSystem`/`FileSystem`, `Engine`, `Error`, `LogQueue`, and Rust `std::fs` for script reading. Filesystem injection allows tests or alternate environments to reuse command execution.

## Risks And Edge Cases
Errors are printed rather than propagated by `run_command`, which is convenient for CLI use but not ideal for programmatic assertions. Dump prints item errors inline and continues iterating. Repair scripts and TryPurge can mutate production data; callers need external backups and clear queue selection.

## Test Signals
Signals include command parse validation, dump output counts/content, consistency-check output, repair behavior under scripting feature tests, and successful purge attempts on existing data directories.
