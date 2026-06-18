<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/main_test.go -->
# sources/user-network-fs/gcsfuse/tools/config-gen/main_test.go

Purpose: Unit tests for `invertMachineTypeGroups`, verifying machine type to group mapping and duplicate detection.

Important APIs, types, and functions: `TestInvertMachineTypeGroups` defines table cases for empty maps, one-to-one, one-to-many, and duplicate machine membership across groups. It uses deferred `recover` to assert expected panics.

Control flow: Each subtest defers a panic checker, calls `invertMachineTypeGroups`, and compares the returned map when no panic is expected.

State and persistence behavior: No file or external state. All data is in-memory maps.

Dependencies and integration points: Depends on `testify/assert` and the generator main package. It validates a helper used before template rendering.

Risks and test signals: Good signal for duplicate group membership, but it does not exercise flag parsing, template execution, or `formatValue`. Panic-based error behavior is intentionally tested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/main_test.go -->
