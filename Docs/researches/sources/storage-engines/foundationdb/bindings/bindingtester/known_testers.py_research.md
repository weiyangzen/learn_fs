# sources/storage-engines/foundationdb/bindings/bindingtester/known_testers.py

## Purpose
This module registers known language binding tester commands and capability constraints.

## Important APIs, Types, And Functions
`COMMON_TYPES` and `ALL_TYPES` define supported tuple value categories. `Tester` stores name, command, max integer bits, API version range, threading support, supported types, and directory snapshot support. `Tester.supports_api_version` checks a version range. `Tester.get_test` resolves a registered tester name or treats an arbitrary string as a command. `_absolute_path` builds paths relative to the bindings tree. `testers` maps Python, Ruby, Java, Java async, Go, Flow, and Swift.

## Control Flow
Imports set `MAX_API_VERSION` from `FDB_API_VERSION`, construct a Java classpath command, and instantiate registry entries with language-specific constraints.

## State And Persistence Behavior
The registry is in-memory and read by `bindingtester.py`. It does not persist data.

## Dependencies And Integration Points
It integrates bindingtester CLI names with built artifacts under `bindings/<language>` and with API/type feature negotiation in `TestRunner`.

## Risks And Edge Cases
Fallback command parsing uses simple string splitting later in the runner. Registry constraints must be updated as bindings gain API/type support. Flow and Swift disable directory snapshot ops.

## Test Signals
Bindingtester startup will fail or reject incompatible options if registry metadata is wrong; external tester invocation failures reveal bad command paths.
