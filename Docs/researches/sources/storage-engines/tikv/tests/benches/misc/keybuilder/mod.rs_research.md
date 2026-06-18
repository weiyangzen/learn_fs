# sources/storage-engines/tikv/tests/benches/misc/keybuilder/mod.rs

## Purpose
This module groups keybuilder microbenchmarks.

## Important APIs, Types, and Functions
It declares `mod bench_keybuilder`.

## Control Flow
No direct runtime logic exists; child module bench functions are registered by the Rust test harness.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It is included by `tests/benches/misc/mod.rs`.

## Risks and Test Signals
Compilation of the misc benchmark target confirms the module path remains valid.
