# sources/storage-engines/tikv/tests/benches/coprocessor_executors/simple_aggr/mod.rs

## Purpose
This module benchmarks simple, no-group aggregation executor cases such as `COUNT(1)` and `COUNT(column)`.

## Important APIs, Types, and Functions
Benchmark functions cover count of a constant, integer column, real column, and bytes column. `Input<M>` carries row count and `SimpleAggrBencher`. `bench` uses bench level to choose row counts and case breadth.

## Control Flow
Cases create fixture columns, build aggregate expression protobufs with `ExprDefBuilder`, and call the configured simple aggregation bencher. Criterion groups are sorted by `BenchCase` names and parameterized by input display strings.

## State and Persistence Behavior
State is in-memory fixture data only. There is no durable engine access in this module.

## Dependencies and Integration Points
It depends on `simple_aggr::util`, shared `FixtureBuilder`/`BenchCase`, TiDB field types, and `tipb::ExprType`. The top-level coprocessor runner calls `simple_aggr::bench`.

## Risks and Test Signals
The benchmark is sensitive to aggregate expression encoding and fixture schema alignment. High bench levels add non-default aggregate cases that catch broader executor construction drift.
