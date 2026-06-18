# sources/storage-engines/wiredtiger/test/packing/CMakeLists.txt

## Purpose
This CMake file declares the WiredTiger packing test executables and registers them with CTest. It covers generic packing, variable-length integer packing, and 4-bit integer-array packing.

## Important APIs, Types, and Functions
The file uses `create_test_executable` to build `test_packing` from `packing-test.c` with executable name `packing-test`, `test_intpack` from `intpack-test3.c` with executable name `intpack-test3`, and `test_int4bpack` from `int4bpack-test.c` with executable name `int4bpack-test`. It registers CTest names `test_packing`, `test_intpack`, and `test_int4bpack`, and labels `test_packing` as `check`.

## Control Flow
CMake creates the three executables, then adds three tests that run the resulting targets. There is no conditional logic, custom config, or direct registration for `intpack-test.c` and `intpack-test2.c`; those files remain auxiliary/manual or historical unless included elsewhere.

## State, Persistence, and Integration
The build file integrates packing tests into the broader WT build system through helper macros. Runtime tests do not need persistent database homes because they exercise internal packing APIs in process.

## Risks and Test Signals
Build risks include source renames, helper macro changes, and tests not being registered or labeled consistently. A notable coverage risk is that only `intpack-test3.c` and `int4bpack-test.c` are registered here, so changes affecting the older `intpack-test.c` and `intpack-test2.c` may not be exercised by this CTest file. CTest pass/fail status is the primary signal.
