# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_unquote.rs

Purpose: implements `JSON_UNQUOTE` and reusable JSON-string escape decoding.

Important APIs/types/functions: `JsonRef::unquote`, `unquote_string`, and private `decode_escaped_unicode`. It defines constants for escaped control characters and uses `ToStringValue`.

Control flow: JSON strings are decoded by scanning chars, treating backslash escapes specially, decoding `\u` followed by exactly four UTF-8 bytes of hex, and ignoring backslashes for unknown escape sequences. Date/datetime/timestamp/time/opaque values are rendered with JSON string formatting and stripped of surrounding quotes. Other JSON types return their normal JSON string representation.

State and persistence: no persistent state. It allocates a result `String` and advances an iterator over the source string.

Dependencies and integration points: used directly by JSON unquote expression behavior and by `path_expr.rs` to decode quoted object keys. Depends on serialization formatting for non-string and temporal values.

Risks: Unicode escape handling decodes one scalar value and does not combine surrogate pairs; invalid or short escapes error. The temporal/opaque branch asserts rendered output has quotes, so formatter behavior is an implicit invariant. Tests cover control escapes, unicode escapes, ignored unknown escapes, incomplete escapes, non-string values, and time/duration unquoting.
