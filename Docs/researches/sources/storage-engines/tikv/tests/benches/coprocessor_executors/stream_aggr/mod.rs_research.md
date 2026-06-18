# sources/storage-engines/tikv/tests/benches/coprocessor_executors/stream_aggr/mod.rs

## Purpose
This module benchmarks stream aggregation where input rows are ordered by group keys.

## Important APIs, Types, and Functions
Cases mirror hash aggregation scenarios: COUNT by integer or decimal group key, two-group variants, two-column integer/real group-by, and COUNT plus FIRST. `Input<M>` carries source rows and a `StreamAggrBencher`.

## Control Flow
Fixtures use ordered column builders for low-cardinality stream cases and sequential columns for one-group-per-row cases. Each benchmark constructs group-by and aggregate expressions, then delegates to the stream aggregation bencher. `bench` chooses representative defaults and adds wider cases by bench level.

## State and Persistence Behavior
No durable state is used. Correct benchmark semantics depend on fixture ordering.

## Dependencies and Integration Points
It depends on `stream_aggr::util`, common benchmark helpers, TiDB field types, and expression builders. It is registered by the coprocessor executor runner.

## Risks and Test Signals
Stream aggregation assumes grouped input order; changing fixture order would alter behavior. Successful Criterion registration and execution across ordered two-group and many-group cases is the useful signal.
