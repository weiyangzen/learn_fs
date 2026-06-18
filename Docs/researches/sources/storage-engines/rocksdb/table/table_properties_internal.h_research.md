# sources/storage-engines/rocksdb/table/table_properties_internal.h

Purpose: declares an internal debug-only helper for randomizing `TableProperties` in tests.

Important APIs/types/functions: `TEST_SetRandomTableProperties(TableProperties* props)` is declared only when `NDEBUG` is not defined.

Control flow: consumers include this header when they need access to the test helper implemented in `table_properties.cc`.

State and persistence behavior: no state is defined here; the function mutates a caller-provided `TableProperties` object in debug builds.

Dependencies/integration points: includes public `rocksdb/table_properties.h` and is used by tests/internal code that validate serialization/equality behavior.

Risks: unavailable in release builds. Its implementation assumes a specific field layout of `TableProperties`, so adding fields requires care.

Test signals: supports internal table-properties tests; no direct test appears in the listed subset.
