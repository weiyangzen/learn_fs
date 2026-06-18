# sources/storage-engines/tikv/tests/benches/coprocessor_executors/selection/mod.rs

## Purpose
This module benchmarks batch selection executor predicates over synthetic columns.

## Important APIs, Types, and Functions
Cases cover `WHERE column`, column-column real comparison, column-constant real comparison, and multiple predicates combining real and integer comparisons. `Input<M>` carries row count and `SelectionBencher`. `bench` registers default and higher-level cases.

## Control Flow
Each case builds fixture columns, constructs predicate expressions with `ExprDefBuilder`, and delegates to the selected bencher. Default runs focus on column-constant comparison over 5000 rows; higher levels add more predicates and smaller row counts.

## State and Persistence Behavior
All state is in-memory fixture data and Criterion measurement state.

## Dependencies and Integration Points
It depends on local `selection::util`, common `BenchCase` and `FixtureBuilder`, TiDB field types, scalar function signatures, and expression builder helpers.

## Risks and Test Signals
The benchmarks assume predicate result types and column indexes match generated fixture schema. Adding higher bench levels is useful for catching less common expression construction regressions.
