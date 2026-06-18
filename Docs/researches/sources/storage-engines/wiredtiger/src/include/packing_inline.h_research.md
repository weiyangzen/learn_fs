# sources/storage-engines/wiredtiger/src/include/packing_inline.h

## Purpose
Implements WiredTiger's struct packing format iterator, size calculation, pack, and unpack logic. It bridges application/key/value format strings, variable-length integer encoding, strings/items, JSON-internal formats, padding, and variadic C APIs.

## Important APIs, Types, And Functions
- `WT_PACK_VALUE` holds one parsed format value, including integer/string/item union, explicit size, size flag, and type.
- `WT_PACK` tracks format iteration state: session, current/end/original pointers, repeat count, and last repeated value.
- `WT_PACK_NAME` tracks generated or configured field names for JSON/projection-style output.
- `__pack_initn`, `__pack_init`, `__pack_name_init`, and `__pack_name_next` initialize iterators and field names.
- `__pack_next` parses the next format item, validates sizes/types, and expands repeated integral types.
- `WT_PACK_GET` extracts variadic arguments into `WT_PACK_VALUE`.
- `__pack_size`, `__pack_write`, and `__unpack_read` compute, write, and read individual values.
- `WT_UNPACK_PUT` writes unpacked values back to variadic output pointers.
- `__wt_struct_packv`, `__wt_struct_sizev`, and `__wt_struct_unpackv` are the va_list versions of the public struct APIs.
- `__wt_struct_size_adjust` adjusts packed sizes when the serialized size field must include its own encoded length.

## Control Flow
Format parsing rejects leading byte-order/alignment markers, skips an optional leading `.`, parses decimal size prefixes, handles padding/string/item/bitfield/integer types, and expands repeat counts for numeric types. Packing fetches each value from `va_list`, computes or writes it according to type, and advances a buffer pointer with size checks. Unpacking mirrors that flow, reading from the input buffer and writing pointers/scalars to caller-provided destinations. Single-character formats take a fast path.

## State And Persistence Behavior
Packing emits persistent byte representations for keys/values and metadata payloads. Integer fields use `intpack_inline.h` to preserve ordering. Strings/items may be fixed-size, null-padded, null-terminated, or length-prefixed depending on type and size prefix. JSON-internal `j/J/K` handling copies through JSON string helpers. The iterator state itself is transient.

## Dependencies And Integration Points
Depends on integer packing, JSON string helpers, config iteration, snprintf, `WT_ITEM`, WiredTiger error macros, and variadic APIs. It integrates with cursor key/value packing, schema formats, JSON conversion, metadata encoding, and record-number formats (`r/R`).

## Risks
The format language is a persistent and public API contract; type semantics must remain compatible. Variadic argument extraction must match C default promotions exactly. Unpacking variable-size `u` without an explicit size consumes remaining input, so callers must provide correct format boundaries. Direct `uint64_t` stores for `R` assume alignment/endianness semantics intended by that internal format. Size calculations need overflow awareness in callers.

## Test Signals
Tests should cover every format character, size prefixes, repeats, padding, JSON internal formats, fixed and variable strings/items, integer ordering, pack/size/unpack round trips, malformed formats, truncated buffers, `__wt_struct_size_adjust`, and API compatibility against known byte encodings.
