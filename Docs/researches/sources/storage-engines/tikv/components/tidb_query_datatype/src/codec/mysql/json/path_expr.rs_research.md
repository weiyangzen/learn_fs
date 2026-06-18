# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs

Purpose: parses MySQL JSON path expressions into reusable typed path legs and flags.

Important APIs/types/functions: `ArrayIndex::{Left, Right}`, `ArraySelection::{Asterisk, Index, Range}`, `KeySelection::{Asterisk, Key}`, `PathLeg`, `PathExpression`, flags `PATH_EXPRESSION_CONTAINS_ASTERISK`, `PATH_EXPRESSION_CONTAINS_DOUBLE_ASTERISK`, `PATH_EXPRESSION_CONTAINS_RANGE`, and `parse_json_path_expr`.

Control flow: nom parsers recognize `$`, dot member selection, quoted/unquoted keys, array indexes including `last` and `last - n`, ranges `start to end`, wildcards, and double-asterisk. Parsing accumulates flags from produced legs, rejects trailing unconsumed input, and rejects a final double-asterisk. Range parsing validates obvious reversed ranges for same-side indexes.

State and persistence: output state is an owned `PathExpression` with a `Vec<PathLeg>` plus bit flags. No persistent state.

Dependencies and integration points: quoted key parsing reuses `json_unquote::unquote_string`; JSON function modules use flags for validation and `extract_json` uses legs for traversal. Nom errors are converted into MySQL-style position messages.

Risks: parser accepts some MySQL-compatible whitespace forms but key grammar must stay aligned with TiDB/MySQL expectations. Quoted keys reject control characters and invalid unicode escapes. Position reporting depends on remaining-input length. Tests are broad: flags, valid paths with unicode keys, `last`, ranges, double-asterisk, invalid syntax, overflow indexes, reversed ranges, asterisk detection, and range detection.
