# sources/storage-engines/wiredtiger/src/support/json.c

## Purpose
`json.c` converts between WiredTiger's packed key/value byte formats and a constrained JSON representation, and provides a tokenizer plus JSON string helpers used by cursor JSON mode. It binds schema column names to packed values so keys and values can be displayed and accepted as named JSON fields.

## Important APIs, Types, and Functions
Primary exported/internal APIs include `__wt_json_alloc_unpack`, `__wt_json_close`, `__wt_json_unpack_str`, `__wt_json_column_init`, `__wt_json_token`, `__wt_json_tokname`, `__wt_json_to_item`, `__wt_json_strlen`, and `__wt_json_strncpy`. Internal helpers include `__json_unpack_char`, `__json_unpack_put`, `__json_struct_size`, `__json_struct_unpackv`, `json_string_arg`, `json_int_arg`, `json_uint_arg`, `__json_pack_struct`, and `__json_pack_size`. The `WT_PACK_JSON_GET` macro maps pack-value types to JSON argument parsers.

## Control Flow
Unpacking initializes a pack iterator and a pack-name iterator, calculates the JSON buffer size by simulating field output, allocates or grows `json->key_buf` or `json->value_buf`, and writes `"name" : value` pairs separated by comma-newline. Strings are escaped with short JSON escapes where possible or `\u00XX` notation for forced byte-oriented output. Packing first validates field names, token order, and value types, computes the packed size, allocates a `WT_ITEM`, and writes packed values into it.

## State and Persistence Behavior
State is stored in `cursor->json_private` as a `WT_JSON` object containing key/value output buffers and key/value column-name config items. `__wt_json_close` frees those buffers and name strings. The tokenizer and string helpers are stateless and operate over caller memory.

## Dependencies and Integration Points
The file depends on WiredTiger pack/unpack internals (`WT_PACK`, `WT_PACK_VALUE`, `__pack_next`, `__pack_write`, `__unpack_read`, `__pack_name_next`), config item naming, cursor URI projection parsing, buffer allocation, hex parsing, character classification, and error-reporting helpers. It integrates with cursor JSON mode and schema metadata describing key/value formats and column names.

## Risks
This is not a general-purpose JSON engine. It tokenizes enough JSON for WiredTiger's schema-shaped representation and accepts only decimal integer forms for integer pack types. Unicode handling is byte-oriented: input `\uXXXX` must fit into `\u00XX` for `__wt_json_strncpy`, and higher Unicode bytes are rejected. Field names and order are validated against schema names, so callers must preserve the generated order. Floating-point tokens are recognized by the tokenizer but are not consumed by the pack macro shown here unless supported elsewhere by format handling. Buffer sizing relies on the sizing pass matching the writing pass exactly.

## Test Signals
Tests should cover JSON unpacking for strings, byte arrays, signed and unsigned integers, recno-like formats, empty strings, embedded control bytes, quotes, backslashes, and column projections. Packing tests should reject wrong field names, missing colons or commas, negative unsigned values, malformed strings, invalid Unicode hex, high-byte Unicode, extraneous trailing input, and destination buffers that are too small. Round-trip tests should compare packed input to JSON and back for representative key/value formats.
