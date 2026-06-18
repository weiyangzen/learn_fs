# sources/storage-engines/tikv/tests/benches/misc/coprocessor/dag/expr/mod.rs

## Purpose
This module groups DAG expression microbenchmarks.

## Important APIs, Types, and Functions
It declares `mod scalar`, which contains scalar-function argument lookup benchmarks.

## Control Flow
Runtime behavior is delegated entirely to the scalar child module's `#[bench]` functions.

## State and Persistence Behavior
This wrapper owns no state.

## Dependencies and Integration Points
It is included by `misc/coprocessor/dag/mod.rs`.

## Risks and Test Signals
Only module path validity is at risk here. Misc bench compilation is the signal.
