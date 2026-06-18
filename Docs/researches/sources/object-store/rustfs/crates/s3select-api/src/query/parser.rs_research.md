# sources/object-store/rustfs/crates/s3select-api/src/query/parser.rs

## Purpose
This file defines the parser abstraction for turning SQL text into a deque of extended statements.

## Important APIs, Types, And Functions
`Parser::parse(&self, sql: &str) -> QueryResult<VecDeque<ExtStatement>>` is the single trait method. A deque is used so dispatchers can preserve statement order and inspect multi-statement input.

## Control Flow
Dispatchers call the parser before planning. They reject multiple statements and empty statement sets after parsing.

## State And Persistence Behavior
The interface is stateless and has no persistence behavior.

## Dependencies And Integration Points
It depends on `ExtStatement` and `QueryResult`. `DefaultParser` in `s3select-query` implements it with DataFusion/sqlparser plus `RustFsDialect`.

## Risks And Edge Cases
The trait permits multi-statement results, but S3 Select execution rejects them later. Parser implementations should preserve errors precisely enough for S3 API error mapping.

## Test Signals
Parser implementation tests cover simple selects, where clauses, multi-statements, semicolons, and syntax errors.
