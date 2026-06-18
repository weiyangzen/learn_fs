# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_extract.rs

Purpose: implements `JsonRef::extract` and shared `extract_json` traversal for MySQL/TiDB JSON path extraction. It returns `None` for no matches, a single owned `Json` for one deterministic match, or an auto-wrapped JSON array when multiple paths, wildcards, double-asterisk, or ranges can produce multiple matches.

Important APIs/types/functions: `JsonRef::extract`, `extract_json`, `RefEqualJsonWrapper`, and `append_if_ref_unique`. It depends on `PathExpression`, `PathLeg`, `ArraySelection`, `ArrayIndex`, `KeySelection`, `JsonType`, and binary accessors such as `array_get_elem`, `object_get_val`, `object_search_key`, and `array_get_index`.

Control flow: `extract` scans all path expressions, records whether multiple matches are possible, recursively calls `extract_json`, then chooses scalar versus array output. `extract_json` consumes one path leg at a time: array legs handle wildcard, index, range, and scalar-as-array-zero compatibility; key legs search objects; double-asterisk first tests the remainder at the current node, then recurses into children with the same full path to implement descendant matching. `append_if_ref_unique` de-duplicates by referenced byte slice pointer within one append operation.

State and persistence: no external persistence. It borrows immutable binary JSON slices and returns owned `Json` copies only at the API boundary. Deduplication state is transient `HashSet` state keyed by backing slice pointers.

Dependencies and integration points: central dependency for `json_length`, `json_keys`, `json_modify`, `json_remove`, and `BinaryModifier`. Correctness relies on binary layout helpers and on path flags computed in `path_expr.rs`.

Risks: recursive wildcard extraction can be expensive on deep or wide documents. Pointer-equality de-duplication avoids duplicate references, not structural equality, so identical values stored in different locations remain distinct. Scalar handling for array index zero is a MySQL compatibility edge that can surprise callers. Tests cover scalar extraction, object keys, wildcards, double-asterisk, repeated paths, ranges, right indexes, and missing paths.
