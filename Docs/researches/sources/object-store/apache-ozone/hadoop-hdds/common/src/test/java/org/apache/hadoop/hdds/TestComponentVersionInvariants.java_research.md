# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/TestComponentVersionInvariants.java

## Purpose
This JUnit 5 parameterized test protects version enum invariants shared by datanode, client, and Ozone Manager component versioning. Other code relies on ordinal ordering and proto integer values to reason about current, default, and future versions.

## APIs and dependencies
The `values()` method returns argument triples for `DatanodeVersion`, `ClientVersion`, and `OzoneManagerVersion`, each as all values, default version, and future version. Tests use the `ComponentVersion` interface and `toProtoValue()`. Dependencies include JUnit Jupiter parameterized tests and the Ozone version enums.

## Control flow and state behavior
Each parameterized test is pure. `testFutureVersionHasTheHighestOrdinal` asserts the future marker is the last enum constant. `testFuturVersionHasMinusOneAsProtoRepresentation` requires future versions to serialize as `-1`. `testDefaultVersionHasZeroAsProtoRepresentation` requires default versions to serialize as `0`. `testAssignedProtoRepresentations` walks every non-future enum value and asserts proto values increase monotonically by one from the default.

## Integration points
The tests defend wire compatibility for protobuf serialization, rolling upgrade behavior, and compatibility gates that compare component versions numerically.

## Risks and test signals
Adding or reordering version enum values can break persisted or wire compatibility if these invariants are not preserved. The final assertion in `testAssignedProtoRepresentations` also encodes an expected gap around `FUTURE_VERSION`; changes to how future values are represented should update this test deliberately, not incidentally.
