# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_merge.rs

Purpose: implements MySQL-compatible JSON merge and merge-patch operations over binary `Json`.

Important APIs/types/functions: `Json::merge`, `Json::merge_patch`, `MergeUnit`, `merge_binary_array`, and `merge_binary_object`. It uses `BTreeMap<String, Json>`, object/array binary accessors, `Json::from_ref_array`, `Json::from_object`, and recursive `Json::merge`.

Control flow: `merge` groups adjacent objects and merges them into a single object, pushes non-objects as merge units, returns a single result directly, or auto-wraps/concatenates into an array. Object merge inserts keys in a `BTreeMap`; duplicate keys merge old and new values recursively. `merge_patch` follows RFC-style patch semantics: non-object patch replaces the target; object patch starts from target object keys, removes keys whose patch value is JSON null, and recursively patches or inserts other keys.

State and persistence: no persistence. The methods allocate owned JSON values for merged objects and arrays. Temporary maps control key ordering and duplicate resolution.

Dependencies and integration points: depends on binary accessors, JSON constructors, and `Error::from` for UTF-8 key conversion. Used by higher-level SQL JSON merge functions.

Risks: `BTreeMap` sorts keys, so output order is deterministic but tied to lexicographic UTF-8 strings. Invalid key bytes error. Recursive duplicate-key merging can allocate heavily for large nested structures. Tests cover adjacent object merge, duplicate keys, scalar/object/array combinations, array concatenation, and nested multi-document merges; merge-patch has no visible local test in this file.
