# sources/storage-engines/wiredtiger/src/include/json.h

## Purpose
Declares `WT_JSON`, a small state holder used when converting between JSON-formatted strings and WiredTiger configuration/format items for cursor keys and values.

## Important APIs, Types, And Functions
- `struct __wt_json` stores `key_buf` and `value_buf`, which own or reference JSON-formatted string buffers.
- `key_names` and `value_names` are `WT_CONFIG_ITEM` slices naming the key and value columns used during conversion.

## Control Flow
This header has no executable logic. It supplies the structure that JSON conversion routines populate and pass around while formatting or parsing cursor key/value material.

## State And Persistence Behavior
The structure is transient per conversion or cursor operation. The buffers may contain serialized user-visible JSON but the struct itself is not a persistent file format. `WT_CONFIG_ITEM` fields are length-delimited slices, so callers must respect length and ownership rather than assuming null-terminated strings.

## Dependencies And Integration Points
Depends on `WT_CONFIG_ITEM` from the config subsystem and integrates with packing/format code that supports JSON strings (`packing_inline.h` internally references JSON string length/copy helpers).

## Risks
The header does not encode ownership rules for `key_buf` and `value_buf`; freeing and reuse must be handled consistently by the conversion implementation. The name fields are slices and can be invalid if the underlying config string expires.

## Test Signals
JSON cursor format tests should cover named and generated key/value columns, non-null-terminated `WT_CONFIG_ITEM` slices, escaped strings, buffer cleanup, and round trips between packed values and JSON output.
