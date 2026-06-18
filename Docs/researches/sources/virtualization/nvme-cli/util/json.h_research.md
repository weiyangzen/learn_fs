# File Research: sources/virtualization/nvme-cli/util/json.h

## Role

`json.h` provides nvme-cli's JSON abstraction layer. When `CONFIG_JSONC` is enabled it wraps json-c APIs with project-specific macros and declares helper functions from `json.c`. When JSON support is disabled it provides no-op stubs so non-JSON builds can compile shared code paths.

## CONFIG_JSONC Enabled

The header includes `<json.h>` and `util/types.h`, then defines convenience macros:

- object/array lifecycle: `json_create_object`, `json_free_object`, `json_free_array`, `json_create_array`;
- object adders for uint, int, uint64, uint128, double, float, string, array, and object values;
- array adders for objects and strings;
- `json_print_object()` using pretty output and `JSON_C_TO_STRING_NOSLASHESCAPE`.

For json-c versions older than the configured 0.14 feature flag, it maps `json_object_new_uint64()` and `json_object_get_uint64()` to local compatibility helpers.

It declares:

- `util_json_object_new_double()`;
- `util_json_object_new_uint64()`;
- `util_json_object_new_uint128()`;
- `util_json_object_get_uint64()`;
- hex/string convenience adders.

There is a duplicate declaration of `util_json_object_new_uint128()`.

## CONFIG_JSONC Disabled

The header forward-declares `struct json_object` and defines macros that either return `NULL`, do nothing, or evaluate selected arguments to avoid unused-variable warnings. This lets callers keep JSON-related code in place without linking json-c.

## Research Notes

This header is designed to keep JSON optional at compile time. The no-op branch is intentionally permissive but has uneven argument evaluation: some macros ignore keys/objects entirely, while others cast only value arguments. Code relying on side effects inside JSON macro arguments would behave differently between JSON and non-JSON builds and should be avoided.
