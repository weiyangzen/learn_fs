# sources/object-store/rustfs/crates/s3select-query/src/sql/logical/optimizer.rs

## Purpose
This file implements logical optimization using DataFusion's optimizer rules.

## Important APIs, Types, And Functions
`DefaultLogicalOptimizer` wraps DataFusion `Optimizer`. `new` builds it with default rules. The API `LogicalOptimizer` implementation optimizes a `QueryPlan` using session state and returns a new `QueryPlan`.

## Control Flow
The optimizer calls DataFusion `optimize` against the plan's `df_plan` and session state/config, preserving `is_tag_scan` in the returned `QueryPlan`.

## State And Persistence Behavior
The optimizer holds rule state in memory only. It produces immutable logical plans.

## Dependencies And Integration Points
It depends on DataFusion optimizer APIs and API `QueryPlan`/`SessionCtx`. `CascadeOptimizer` runs it after analysis and before physical planning.

## Risks And Edge Cases
Logical optimizer behavior is tightly coupled to DataFusion version and may rewrite scans/filters in ways that interact with custom parquet access planning. `is_tag_scan` is only preserved, not interpreted.

## Test Signals
Covered indirectly through query execution tests and DataFusion plan success/failure.
