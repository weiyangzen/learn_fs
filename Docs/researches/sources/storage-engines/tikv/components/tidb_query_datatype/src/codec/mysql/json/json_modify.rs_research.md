# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_modify.rs

Purpose: provides the public JSON modification entry point for `JSON_INSERT`, `JSON_REPLACE`, and `JSON_SET`.

Important APIs/types/functions: `ModifyType::{Insert, Replace, Set}` and `JsonRef::modify`. It uses `PathExpression`, `BinaryModifier`, and owned `Json` replacement values.

Control flow: the function first checks that path count equals value count, rejects any path containing wildcard/double-asterisk or range, copies `self` into `res`, and then applies each path/value pair sequentially. For each pair it constructs a fresh `BinaryModifier` over the current result and dispatches to `insert`, `replace`, or `set`.

State and persistence: no external persistence. Sequential modification means later operations see earlier changes. The original JSON is not mutated; each operation produces a new owned binary JSON.

Dependencies and integration points: delegates actual binary rewriting and insert/replace semantics to `modifier.rs`, while path validation comes from `path_expr.rs`.

Risks: parameter-count diagnostics use expected/found values that are easy to misread because expected is the value count. Rebuilding after every path can be expensive for many modifications. Wildcard/range rejection is required for MySQL behavior and must remain aligned with the parser flags. Tests cover root set, object and array edits, scalar auto-wrap, ignored inserts/replaces, missing parents, and wildcard errors.
