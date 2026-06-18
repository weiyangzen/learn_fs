# sources/storage-engines/raft-engine/examples/fork.rs

## Purpose
Minimal command-line example for forking/copying a raft-engine directory from a source path to a target path.

## Important APIs, Types, And Functions
Uses `Config`, `Engine::<_, _>::fork`, `DefaultFileSystem`, `Arc`, and basic `std::env::args` parsing.

## Control Flow
The program prints usage, reads source and target positional arguments, builds a default config with `dir` set to the source, constructs a default filesystem, calls `Engine::fork`, unwraps errors, and prints success.

## State And Persistence Behavior
The source engine directory is read and the target directory is populated by `Engine::fork`. The example does not open the copied engine afterward or validate contents.

## Dependencies And Integration Points
Integrates with the engine fork API, default filesystem abstraction, and path handling. It is useful as a runnable example for backup/copy workflows.

## Risks And Edge Cases
Argument parsing is intentionally minimal and panics on missing arguments. There is no overwrite protection or validation in this wrapper beyond whatever `Engine::fork` enforces. All errors panic through `unwrap`.

## Test Signals
Signals are successful example build and a manual run producing `success!` with a usable target directory.
