# sources/storage-engines/tikv/tests/benches/coprocessor_executors/selection/util.rs

## Purpose
This utility module adapts `BatchSelectionExecutor` into the shared Criterion bench interface.

## Important APIs, Types, and Functions
`SelectionBencher<M>` defines benchmark naming, execution, and clone-boxing. `BatchBencher` implements it by wrapping a cloned `BatchFixtureExecutor` and predicate vector in `BatchSelectionExecutor`.

## Control Flow
For each benchmark iteration, the fixture is cloned, an `EvalConfig` is allocated, expressions are cloned, and the batch selection executor is drained through `BatchNextAllBencher`.

## State and Persistence Behavior
No persistent state is used; executor and fixture state are per iteration.

## Dependencies and Integration Points
It depends on `criterion`, `BatchSelectionExecutor`, `EvalConfig`, `tikv::storage::Statistics`, and shared bencher/fixture utilities.

## Risks and Test Signals
`unwrap()` surfaces unsupported or malformed expressions. Benchmark output under the `batch` name is the main signal that the selection executor still builds and drains correctly.
