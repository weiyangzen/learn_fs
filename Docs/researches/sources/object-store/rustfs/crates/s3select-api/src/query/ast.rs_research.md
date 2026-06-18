# sources/object-store/rustfs/crates/s3select-api/src/query/ast.rs

## Purpose
This file defines the API crate's extensible statement wrapper. It currently wraps DataFusion/sqlparser statements while leaving room for future non-SQL or RustFS-specific commands.

## Important APIs, Types, And Functions
`ExtStatement::SqlStatement(Box<Statement>)` is the only variant. The enum derives debug, clone, equality, and ordering-compatible equality semantics for parser and planner handoff.

## Control Flow
Parser implementations convert SQL text into `ExtStatement` values. Logical planners match the wrapper and translate the contained `Statement` into a DataFusion logical plan.

## State And Persistence Behavior
The enum is an in-memory AST carrier and has no persistent state.

## Dependencies And Integration Points
It depends on DataFusion's re-exported `sqlparser::ast::Statement`. It is consumed by the parser trait and by `LogicalPlanner::create_logical_plan`.

## Risks And Edge Cases
Only SQL is represented today, so any future S3 Select-specific command syntax must add variants and update parser, planner, dispatcher, and tests together.

## Test Signals
Parser tests in `s3select-query/src/sql/parser.rs` validate that normal SQL text produces this wrapper.
