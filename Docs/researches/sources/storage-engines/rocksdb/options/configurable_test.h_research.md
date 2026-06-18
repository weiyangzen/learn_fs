# sources/storage-engines/rocksdb/options/configurable_test.h

## Purpose
`configurable_test.h` provides reusable scaffolding for configurable option tests: small option structs, metadata maps, enum mappings, mode flags, and a templated configurable base.

## Important APIs, Types, and Functions
Definitions include `TestEnum`, `test_enum_map`, `TestOptions`, `simple_option_info`, `enum_option_info`, `unique_option_info`, `shared_option_info`, `pointer_option_info`, `TestConfigMode`, and `TestConfigurable<T>`. The template derives from `Configurable` and exposes `unique_`, `shared_`, and raw `pointer_` members for nested tests.

## Control Flow
The constructor registers simple and enum option maps depending on mode bits. Derived classes add unique/shared/raw nested registrations. The destructor deletes the raw pointer member, allowing raw-pointer configuration tests without leaks.

## State and Persistence Behavior
All state is in-memory test state. The option maps use the same offset-based metadata pattern as production code, so parsing and serialization exercise real `OptionTypeInfo` behavior.

## Dependencies and Integration Points
It includes `configurable_helper.h`, `rocksdb/configurable.h`, and `rocksdb/utilities/options_type.h`, and is consumed by `configurable_test.cc`.

## Risks
The header's static maps are intended only for tests. Raw pointer ownership is manual and depends on the scaffold destructor. Extending this into multiple production-like translation units would not be appropriate.

## Test Signals
The executable coverage lives in `configurable_test.cc`, which uses this scaffold across simple, enum, unique, shared, raw, nested, and mutable modes.
