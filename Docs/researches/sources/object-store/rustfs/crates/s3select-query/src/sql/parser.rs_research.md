# sources/object-store/rustfs/crates/s3select-query/src/sql/parser.rs

## Purpose
This file implements SQL parsing for RustFS S3 Select using DataFusion/sqlparser with `RustFsDialect`.

## Important APIs, Types, And Functions
`DefaultParser` implements the API `Parser` trait. `ExtParser` wraps `sqlparser::Parser`. `parse_sql` uses `RustFsDialect`; `parse_sql_with_dialect` tokenizes SQL, ignores empty semicolon-separated statements, parses statements into `ExtStatement::SqlStatement`, and errors when a statement delimiter is missing. The `parser_err!` macro builds parser errors.

## Control Flow
Parsing tokenizes input, repeatedly consumes extra semicolons, stops at EOF, parses one statement at a time, and enforces that non-EOF tokens after a parsed statement must be semicolon-delimited. The dispatcher later rejects multiple statements.

## State And Persistence Behavior
Parser state is transient token/parser state. `DefaultParser` is zero-sized and safe to share.

## Dependencies And Integration Points
It depends on DataFusion/sqlparser tokens, tokenizer, parser errors, SNAFU `ParserSnafu`, API `ExtStatement`, and `RustFsDialect`. `SimpleQueryDispatcher` uses it for all SQL input.

## Risks And Edge Cases
Empty SQL parses to an empty deque and is converted to a parser error by the dispatcher. Multiple statements parse successfully here and are rejected later. The parser mostly delegates syntax support to DataFusion/sqlparser, so S3 Select dialect gaps require custom parsing extensions.

## Test Signals
Unit tests cover parser creation, simple select, selected columns, where clauses, and related parse behavior. Error-handling tests cover invalid syntax, empty SQL, multi-statement rejection, unsupported DML/DDL, and long queries.
