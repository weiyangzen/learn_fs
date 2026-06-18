# sources/storage-engines/wiredtiger/test/model/src/include/model/data_value.h

Purpose: declaration of the model's generic key/value type and cursor conversion API.

Important APIs and types: `byte_vector` represents arbitrary WT_ITEM bytes. `base_data_value` is a `std::variant<std::monostate, int64_t, uint64_t, std::string, byte_vector>`. `data_value` inherits the variant, provides `create_none`, `unpack` overloads for raw buffer, byte vector, string, and `WT_ITEM`, `none`, and `wt_type`. Constants `NONE` and `ZERO` are declared. Stream operators and cursor helpers `get_wt_cursor_key/value` and `set_wt_cursor_key/value` are declared.

Control flow and state: the header defines value semantics only; concrete conversion behavior lives in `data_value.cpp`. `NONE` is represented by `std::monostate` and is used throughout the model as deleted/not-found sentinel.

Dependencies and integration: includes `model/core.h`, `wiredtiger.h`, and standard variant/vector/string headers. Used by tables, updates, workload operations, verification, and WT runner cursor code.

Risks and test signals: inheriting from `std::variant` exposes variant operations directly, which is convenient but broad. Only single-field WT formats are currently supported by implementation. Correct equality/order behavior from the variant is central to `std::map<data_value, kv_table_item>` and verification ordering.
