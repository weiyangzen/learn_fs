# File Research: sources/virtualization/nvme-cli/util/json.c

## Role

`json.c` implements helper wrappers around json-c for nvme-cli output formatting. It fills compatibility gaps for older json-c versions, serializes wide numeric values, and provides convenience functions for common hex/string representations.

## Numeric Object Helpers

- `util_json_object_new_double()` formats a `long double` with `%Lf`, stores it as a JSON string, and returns the json-c object.
- `util_json_object_new_uint64()` formats a `uint64_t` with `PRIu64`, stores it as a JSON string, and returns it. `json.h` maps `json_object_new_uint64` to this helper when `CONFIG_JSONC_14` is unavailable.
- `util_json_object_new_uint128()` converts `nvme_uint128_t` with `uint128_t_to_string()`, stores it as a string, then installs `util_json_object_string_to_number()` as a custom serializer so JSON output is emitted as an unquoted number.
- `util_json_object_get_uint64()` only parses objects that are strings, using `strtoull()` in base 10, and returns zero on parse failure.

## Formatting Adders

- `json_object_add_uint_02x()` delegates to `json_object_add_uint_0nx()` with width 2.
- `json_object_add_uint_0x()` adds a string like `0x%x`.
- `json_object_add_byte_array()` emits an input byte buffer as a reversed-order hex string with `0x` prefix; missing data becomes `"No information provided"` and allocation failure becomes `"Could not allocate string"`.
- `json_object_add_nprix64()` emits a `uint64_t` using `%#` hex formatting.
- `json_object_add_uint_0nx()` and `json_object_add_0nprix64()` add zero-padded hex strings.
- `json_object_add_string()` uses `vasprintf()` to build a formatted string value and falls back to `"Could not allocate string"`.

## Dependencies

- `json.h` for wrapper macros and json-c declarations.
- `types.h` for `nvme_uint128_t`, `STR_LEN`, and conversion helpers.
- `cleanup.h` for `__cleanup_free`.
- json-c internals such as `struct printbuf` for the custom serializer callback.

## Research Notes

Most helpers deliberately store numbers as strings to preserve precision or formatting. The uint128 helper is the exception at output time: it uses a string internally but serializes as a bare number. Callers should not assume `util_json_object_get_uint64()` handles json-c integer objects; this implementation only extracts string objects.
