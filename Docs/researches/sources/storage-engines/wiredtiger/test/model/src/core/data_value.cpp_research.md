# sources/storage-engines/wiredtiger/test/model/src/core/data_value.cpp

Purpose: implementation of the model's generic key/value representation and WiredTiger cursor conversion helpers.

Important APIs and functions: defines constants `NONE` and `ZERO`. `data_value::unpack` decodes a raw buffer with a single WiredTiger format character into `int64_t`, `uint64_t`, `std::string`, or `byte_vector` using `__wt_struct_unpack`. `wt_type` maps variant alternatives back to WT format strings. Stream operators print byte vectors as hex and values in human-readable form. `get_wt_cursor_key/value` and `set_wt_cursor_key/value` bridge `WT_CURSOR` varargs APIs using cursor key/value formats.

Control flow and state: all conversion paths reject null buffers, null/empty formats, multi-field structs, unsupported `x`, and type mismatches. Length prefixes are skipped before checking the single format character. `WT_ITEM` values are copied to/from `byte_vector` and temporary `WT_ITEM`.

Dependencies and integration: depends on `model/data_value.h`, `model/util.h::parse_uint64`, WiredTiger public API, and internal `__wt_struct_unpack`.

Risks and test signals: the model currently does not support compound formats or type `x`; workload generation is similarly narrow. Cursor setters require exact variant/type compatibility and reject `NONE`. Verification and log replay heavily depend on these conversions matching WiredTiger packing behavior.
