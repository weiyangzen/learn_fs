# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/exceptions/TestResultCodes.java

Purpose: verifies ordinal and name alignment between `OMException.ResultCodes` and protobuf `OzoneManagerProtocolProtos.Status`.

Important APIs/types/functions: iterates `ResultCodes.values()` and `Status.values()`, checks equal enum counts, matching names by ordinal, and round-trip conversion through protobuf ordinal.

Control flow and state: no mutable state. The test loops all enum entries and fails on length mismatch, name mismatch, or conversion mismatch.

Dependencies and integration points: ties Java exception result codes to wire-level OM response statuses. Many protocol paths rely on ordinal compatibility when converting status values.

Risks and test signals: catches dangerous enum insertion/reordering in either Java or protobuf definitions. This is a persistence and compatibility risk because status ordinals may be serialized or mapped across client/server boundaries.
