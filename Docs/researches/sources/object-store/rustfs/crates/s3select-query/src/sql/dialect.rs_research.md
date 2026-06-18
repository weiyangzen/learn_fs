# sources/object-store/rustfs/crates/s3select-query/src/sql/dialect.rs

## Purpose
This file defines the SQL dialect accepted by the RustFS S3 Select parser.

## Important APIs, Types, And Functions
`RustFsDialect` implements `sqlparser::Dialect`. Identifier starts may be alphabetic, `_`, `#`, or `@`. Identifier parts may also include ASCII digits, `$`, `#`, `_`, and `@`. `supports_group_by_expr` returns true.

## Control Flow
The parser passes this dialect to DataFusion/sqlparser tokenization and parsing, allowing S3 Select-style pseudo columns such as `_1` and special identifier prefixes.

## State And Persistence Behavior
The dialect is zero-sized and stateless.

## Dependencies And Integration Points
It depends on DataFusion's sqlparser dialect trait and is used by `ExtParser::parse_sql`.

## Risks And Edge Cases
The dialect allows broad Unicode alphabetic starts but only ASCII digits in identifier parts. `$` is allowed after the first character but not at the start. Changes can break CSV header aliases and parser compatibility.

## Test Signals
Extensive unit tests cover construction, debug output, valid/invalid identifier starts and parts, Unicode letters, control characters, digit handling, consistency, memory size, and trait behavior.
