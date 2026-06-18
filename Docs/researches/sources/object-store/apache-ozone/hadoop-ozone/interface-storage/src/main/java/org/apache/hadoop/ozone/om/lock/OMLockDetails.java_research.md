# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/OMLockDetails.java

Purpose: Mutable timing/result object describing an OM lock operation.

Important APIs/types/functions: Static empty acquired/not-acquired instances, fields for `lockAcquired`, wait/read/write nanos, `add(long, LockOpType)`, `merge(OMLockDetails)`, getters/setters, `toProtobufBuilder()`, `toString()`, and `clear()`. Internal enum `LockOpType` classifies wait/read/write timing.

Control flow, state, and persistence: Accumulates timing across lock operations and can serialize to `OMLockDetailsProto` from `OmClientProtocol.proto`. It is runtime state carried in responses/logging/metrics rather than DB-persisted state.

Dependencies and integration points: Returned by `IOzoneManagerLock` operations, used by request code to capture lock timing, and converted to client protocol protobuf for observability.

Risks: Static `EMPTY_DETAILS_*` instances are mutable because `clear`, setters, and `merge` are public; callers must avoid mutating shared constants. `merge` overwrites `lockAcquired` with the merged object while adding timings, which is meaningful but can surprise callers aggregating mixed results.

Test signals: No direct unit test in this subset. Proto field definition exists in `OmClientProtocol.proto`.
