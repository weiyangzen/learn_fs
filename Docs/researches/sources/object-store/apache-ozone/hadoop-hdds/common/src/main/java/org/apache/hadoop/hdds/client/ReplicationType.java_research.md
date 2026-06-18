## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationType.java

Purpose: client-facing replication type enum.

Important APIs: enum values `RATIS`, `STAND_ALONE`, deprecated `CHAINED`, and `EC`; `fromProto` and `toProto` bridge to HDDS protobuf enums.

Control flow: null conversions return null; known values switch explicitly; unsupported proto/type values throw. State/persistence: enum constants only. Dependencies: HDDS protobufs.

Integration points: parsing, serialization, client API, replication validation. Risks: deprecated `CHAINED` remains serializable; enum name alignment with protobuf is relied on elsewhere; new proto values require code changes. Test signals: all enum conversions, null handling, deprecated CHAINED compatibility, and invalid-value behavior.
