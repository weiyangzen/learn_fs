# sources/object-store/rustfs/crates/s3select-query/src/test/error_handling_test.rs

## Purpose
This file tests error handling across the query engine for invalid SQL, multi-statements, unsupported operations, invalid references, empty input, long SQL, and injection-like patterns.

## Important APIs, Types, And Functions
`create_test_input_with_sql` builds CSV `SelectObjectContentInput` values with `FileHeaderInfo::USE`. Tests use `get_global_db`, `Query`, `Context`, and `QueryError`.

## Control Flow
Each test creates a database in test mode, builds a query, executes it, and asserts either an expected error variant or graceful success/failure. Multi-statement tests specifically match `QueryError::MultiStatement`. Empty-query tests expect parser errors.

## State And Persistence Behavior
All tests run against in-memory fixture sessions through `get_global_db(..., true)`. No persistent state is mutated.

## Dependencies And Integration Points
The tests cover parser, dispatcher validation, metadata/planner resolution, and execution error propagation. They use `s3s` DTOs and the public crate API.

## Risks And Edge Cases
Several tests allow either success or error for invalid column references, long queries, and injection-like patterns, so they mainly assert graceful handling rather than strict semantics. They do not inspect S3 API error code mapping.

## Test Signals
Strong signal exists for syntax errors, multi-statement rejection, unsupported DML/DDL rejection, empty SQL parser errors, and complex invalid query failure.
