# sources/storage-engines/tikv/components/memory_trace_macros/Cargo.toml

## Purpose
This manifest defines `memory_trace_macros`, a proc-macro crate for deriving memory tracing helper methods.

## Important APIs, Types, and Functions
The manifest marks the library as `proc-macro = true` and depends on `quote` and `syn` with full AST parsing and extra traits.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
The generated code references `tikv_alloc::trace::TraceEvent`, but the macro crate itself only needs `syn` and `quote`.

## Risks
Proc-macro crates are compiled and run at build time. Dependency changes can affect generated code compatibility and compiler error quality.

## Test Signals
No local tests are present in the manifest.
