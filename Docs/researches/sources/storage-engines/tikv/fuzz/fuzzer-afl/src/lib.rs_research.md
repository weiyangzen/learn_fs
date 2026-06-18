# sources/storage-engines/tikv/fuzz/fuzzer-afl/src/lib.rs

## Purpose
Placeholder library module that keeps Cargo satisfied for the AFL fuzzer package while actual fuzzer binaries are generated dynamically.

## Important APIs, Types, and Functions
No public API beyond crate existence. The file contains documentation explaining generated binaries come from `fuzz/cli.rs`.

## Control Flow
Cargo can compile the package even when no generated `src/bin` target exists.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Pairs with `fuzzer-afl/template.rs` and the CLI's source generation. It prevents an empty package from being structurally invalid.

## Risks
No behavioral risk; stale comments could mislead if generation moves.

## Test Signals
`cargo check -p fuzzer-afl` should succeed before and after generated binaries are created.
