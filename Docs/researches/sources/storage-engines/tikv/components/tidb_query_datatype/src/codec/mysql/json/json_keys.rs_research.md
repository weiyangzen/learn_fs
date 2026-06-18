# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_keys.rs

Purpose: implements `JSON_KEYS` behavior for a binary `JsonRef`, optionally scoped by one path expression.

Important APIs/types/functions: `JsonRef::keys` is public; private `json_keys` builds the result. It uses `PathExpression::contains_any_asterisk`, `JsonRef::extract`, `JsonType::Object`, `object_get_key`, `Json::from_str_val`, and `Json::from_array`.

Control flow: with no path, `json_keys(self)` returns an array of object keys or `None` for non-objects. With a path, the method rejects more than one expression and rejects wildcard/double-asterisk paths, extracts the target, and returns keys only when the target exists and is an object.

State and persistence: no persistent state. It creates a transient `Vec<Json>` sized to the object element count and copies key bytes into JSON string values.

Dependencies and integration points: relies on `json_extract.rs` for path resolution and binary object accessors for key ordering. The function is exposed through the `JsonRef` extension imported by the JSON module.

Risks: keys are decoded with `str::from_utf8`, so invalid key bytes propagate as errors. Ordering follows binary object order, which is normally sorted by construction. Path validation forbids wildcards because MySQL `JSON_KEYS` only accepts zero or one non-wildcard path. Tests cover non-object `None`, object keys, scoped object extraction, missing paths, arity errors, and wildcard rejection.
