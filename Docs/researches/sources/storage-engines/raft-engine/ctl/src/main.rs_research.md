# sources/storage-engines/raft-engine/ctl/src/main.rs

## Purpose
Small binary entry point for the raft-engine control tool.

## Important APIs, Types, And Functions
Imports `clap::Parser` and `raft_engine_ctl::ControlOpt`. `main` initializes `env_logger`, parses command-line arguments, and invokes `ControlOpt::validate_and_execute`.

## Control Flow
Startup is linear: initialize logging, parse args into `ControlOpt`, execute, and print the debug representation of any returned error.

## State And Persistence Behavior
The binary itself owns no persistent state. The selected subcommand may read or mutate raft-engine directories through the library layer.

## Dependencies And Integration Points
Integrates with the library parser in `ctl/src/lib.rs`, Clap-derived CLI metadata, environment logging configuration, and all underlying `Engine` tooling APIs.

## Risks And Edge Cases
The process exits with success even after printing an error because `main` does not set a non-zero exit code. That can hide failures in shell automation unless stdout/stderr is inspected.

## Test Signals
Build success and CLI smoke tests are the useful signals. Behavioral coverage mostly belongs to `ctl/src/lib.rs` and engine tool tests.
