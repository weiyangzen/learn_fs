# sources/storage-engines/tikv/tests/benches/coprocessor_executors/top_n/mod.rs

## Purpose
This module benchmarks batch TopN executor sorting and limiting behavior over different projection widths and order-by expression counts.

## Important APIs, Types, and Functions
Helper functions build one-order-by and three-order-by cases with configurable projection column count and limit. Cases include 1 or 50 columns with limit 10 or 4000, and three-key ordering using `IntIsNull`, ascending column, and descending column. `Input<M>` carries row count and `TopNBencher`.

## Control Flow
Each benchmark builds random integer columns, constructs order-by expressions, and delegates to the selected bencher. Default cases cover three-key ordering; higher bench levels add simpler one-key variants and small row counts.

## State and Persistence Behavior
All benchmark data is in-memory fixture state.

## Dependencies and Integration Points
It depends on `top_n::util`, common `FixtureBuilder`/`BenchCase`, TiDB field types, scalar signatures, and expression builders.

## Risks and Test Signals
The cases stress comparator construction, multi-column projection retention, descending order flags, and large limit handling. `assert!` guards invalid helper inputs.
