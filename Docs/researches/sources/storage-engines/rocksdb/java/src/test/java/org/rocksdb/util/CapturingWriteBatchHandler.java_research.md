# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/CapturingWriteBatchHandler.java

Purpose: Test `WriteBatch.Handler` implementation that records every write-batch callback as an `Event` for assertions.

Important APIs/types/functions: overrides `put`, `merge`, `delete`, `singleDelete`, `deleteRange`, `logData`, `putBlobIndex`, prepare/commit marker methods, `getEvents`, nested `Event`, and `Action` enum.

Control flow and state: each callback appends a new `Event` to an internal `ArrayList`. `getEvents()` returns a copy of the event list. `Event.equals` compares action, column family id, and byte-array contents with `Arrays.equals`; `hashCode` mirrors that state.

State and persistence behavior: entirely in-memory test capture. Events keep references to byte arrays rather than copies, so later mutation by tests can change captured content.

Dependencies and integration points: used by tests invoking `WriteBatch.iterate(handler)` to verify JNI callback order and payloads.

Risks: `putBlobIndex(int, key, value)` drops the supplied column family id and records default id through the two-argument constructor. Transaction marker callbacks ignore XIDs/timestamps, so the helper only asserts marker type presence, not payload.

Test signals: downstream write batch tests use this as an oracle for callback ordering and action classification.
