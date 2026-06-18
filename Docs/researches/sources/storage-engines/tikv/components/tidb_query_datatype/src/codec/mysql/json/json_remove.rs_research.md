# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_remove.rs

Purpose: implements MySQL `JSON_REMOVE` behavior over binary JSON.

Important APIs/types/functions: public `JsonRef::remove`, `BinaryModifier::remove`, and `PathExpression` validation helpers.

Control flow: it rejects paths that are the root, contain wildcard/double-asterisk, or contain ranges. Starting from an owned copy of `self`, it applies each removal sequentially through a new `BinaryModifier`. Missing paths are treated as no-ops by the modifier.

State and persistence: no persistent state. Like modification, each removal produces an owned `Json`, and subsequent removals operate on the previous output.

Dependencies and integration points: depends on `modifier.rs` for structural removal and `json_extract.rs` indirectly through the modifier. It is part of the JSON mutation API surface.

Risks: sequential path application means indexes can shift after earlier removals, matching MySQL semantics but requiring careful tests. Root removal is invalid. Wildcards and ranges are forbidden. Tests cover array element deletion, object member deletion, nested object deletion, no-op missing parents, and invalid wildcard paths.
