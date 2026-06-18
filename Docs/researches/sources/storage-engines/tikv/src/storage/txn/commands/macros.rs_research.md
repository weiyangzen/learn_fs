# sources/storage-engines/tikv/src/storage/txn/commands/macros.rs

## Purpose
Provides local macros that standardize transaction command struct generation and `CommandExt` boilerplate. These macros keep all command files aligned on context, deadlines, heap sizing, metrics, byte accounting, and latch generation.

## Important APIs, Types, and Functions
`command!` emits a public command struct with `ctx`, `deadline`, declared fields, a `new` constructor returning `TypedCommand`, `HeapSize`, and optional `Display`/`Debug`. `ctx!` implements context access and deadline. `ts!`, `tag!`, `request_type!`, `write_bytes!`, `gen_lock!`, and `property!` generate common `CommandExt` methods.

## Control Flow
The generated constructor chooses `DEFAULT_EXECUTION_DURATION_LIMIT` unless `ctx.max_execution_duration_ms` overrides it, then wraps the struct in the matching `Command` enum variant and converts to `TypedCommand`. Display formatting appends approximate heap size.

## State and Persistence
Macros do not persist state directly. They shape command metadata that affects scheduler deadlines, metrics counters, latch coverage, memory tracking, flow-control byte estimates, and readonly/pipelining flags.

## Dependencies and Integration Points
The macros depend on every generated command having a same-named `Command` enum variant. They bind to `crate::storage::Context`, `tikv_util::deadline::Deadline`, `tikv_util::memory::HeapSize`, storage metrics, tracker request types, and transaction latches.

## Risks and Test Signals
Because the macros hide boilerplate, incorrect macro use can silently produce wrong latch keys, write-byte accounting, or request types. The `display` pattern also allows field sub-methods such as `.len`. Coverage is indirect through all command-specific tests and compile-time expansion.
