# sources/test-tools/fio/json.h

Purpose: declares fio's lightweight JSON tree structures and convenience builders. It is an output-building API, not a parser.

Important APIs/types: integer constants for value and parent types; `struct json_value`, `json_array`, `json_object`, and `json_pair`; object/array constructors; `json_free_object`; typed add wrappers for int, float, string, object, and array; `json_array_last_value_object`; and `json_print_object`.

Control flow/state: inline wrappers construct a temporary `json_value` descriptor and delegate to the generic add functions in `json.c`, which allocate the owned tree nodes. Parent pointers in values, arrays, objects, and pairs allow the printer to derive indentation depth.

Dependencies/integration: includes `lib/output_buffer.h` because printing targets `struct buf_output`. The header is consumed by fio output/stat formatting code that needs hierarchical JSON construction.

Risks/test signals: the API does not expose `json_free_array` for standalone arrays, so top-level ownership is expected to be an object. `json_array_last_value_object` assumes the array is non-empty and the last value is an object. Tests should cover wrapper behavior for null strings and ownership expectations for nested arrays/objects.
