## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ECReplicationConfig.java

Purpose: immutable erasure-coding replication config implementing `ReplicationConfig`.

Important APIs: constructors from data/parity defaults, explicit codec/chunk size, string format, and proto; enum `EcCodec` with `RS` and `XOR`; getters; `toProto`; `getRequiredNodes` as data plus parity; `getMinimumNodes` as data; string/config formats.

Control flow: string parsing uses regex `<codec>-<data>-<parity>-<chunksize>[k]`, validates known codec and positive data/parity/chunk size, and multiplies chunk size by 1024 if a `k` suffix exists. Proto constructor trusts proto values except enum conversion.

State/persistence: final fields; serializes into `HddsProtos.ECReplicationConfig`. Dependencies: Jackson, regex, HDDS protobufs, JCIP immutable annotation.

Integration points: `ReplicationConfig.parse`, `DefaultReplicationConfig`, OM/SCM replication validation, client API display. Risks: integer overflow when multiplying large chunk sizes by 1024; `chunkKB()` truncates non-KB-aligned proto chunk sizes; proto constructor can create zero/negative configs if upstream data is invalid; default validation pattern restricts allowed EC combinations elsewhere, not here. Test signals: accepted string formats/case, invalid codec and non-positive numbers, proto round trip, chunk suffix behavior, overflow boundaries, and validator integration.
