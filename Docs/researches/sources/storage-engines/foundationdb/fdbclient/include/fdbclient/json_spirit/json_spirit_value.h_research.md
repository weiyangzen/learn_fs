<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_value.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_value.h

## Purpose
`json_spirit_value.h` defines the json_spirit in-memory JSON value model, including vector-backed and map-backed object configurations for narrow and wide strings.

## Important APIs, Types, and Functions
Important exports include `Value_type`, `Null`, template `Value_impl<Config>`, `Pair_impl<Config>`, `Config_vector`, `Config_map`, typedefs `Value`, `Pair`, `Object`, `Array`, `wValue`, `mValue`, and `wmValue` when enabled, `to_str`, typed getters, constructors from JSON-compatible types and compatible Boost variants, and `value_type_to_string`.

## Control Flow
`Value_impl` stores data in a Boost variant containing object, array, string, bool, signed integer, real, null, or unsigned integer. Constructors normalize `int` to `int64_t` and keep `uint64_t` distinguishable while reporting it as `int_type`. Getters check the active JSON type and throw `std::runtime_error` with type names on mismatch. Config classes define whether objects append duplicate names in a vector or assign by key in a map.

## State and Persistence Behavior
Values are ordinary in-memory objects with recursive Boost variant storage. They do not persist directly. The typedef selection macros enable all narrow/wide and vector/map value models in this copy, affecting compile-time surface and object behavior.

## Dependencies and Integration Points
The file depends on STL containers and strings, assertions, streams, standard exceptions, Boost config, integer types, shared pointers, and variant. Reader and writer templates use these value models to parse and emit JSON for FoundationDB components that still rely on json_spirit.

## Risks and Edge Cases
`get_int` narrows `int64_t` to `int`, and signed/unsigned conversions in `get_int64` and `get_uint64` can wrap if callers ask for the wrong width. Vector-backed objects preserve duplicate keys, while map-backed objects overwrite by name. Enabling all value variants increases compile cost. Type checking happens at runtime rather than compile time.

## Test Signals
Signals include construction and typed getter tests, signed/unsigned boundary tests, vector versus map object duplicate-key behavior, parser/writer round trips, wide-string builds, and type mismatch exception tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_value.h -->
