# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/modifier.rs

Purpose: performs low-level binary JSON rewriting for insert, replace, set, and remove operations.

Important APIs/types/functions: `BinaryModifier<'a>`, `new`, `set`, `replace`, `insert`, `remove`, private `do_insert`, `do_remove`, `rebuild`, and recursive `rebuild_to`. It tracks `old: JsonRef`, `to_be_modified_ptr: *const u8`, and `new_value: Option<Json>`.

Control flow: public operations locate target or parent nodes with `extract_json`, record the backing pointer of the node to replace, prepare a new owned JSON value when needed, and call `rebuild`. Insert can append to arrays, auto-wrap scalar parents into arrays for array index insertions, or insert object keys. Remove rebuilds arrays without the selected index or objects without the selected key. `rebuild_to` walks the original binary tree, copies headers and keys, recursively rewrites child value entries, and updates value type/offset metadata.

State and persistence: state is transient and pointer-based. It never mutates the input buffer; it emits a new `Json` with rebuilt bytes.

Dependencies and integration points: used by `json_modify.rs` and `json_remove.rs`; relies heavily on binary layout constants, `NumberCodec`, value-entry decoding, and pointer identity from `JsonRef`.

Risks: raw pointer identity is central; any future representation that moves buffers during traversal would break it. Offset and inline-literal rewriting is delicate. Multiple matches use only the first match. Rebuild cost is proportional to document size even for small edits. Behavior is tested indirectly through modify/remove tests rather than direct modifier unit tests.
