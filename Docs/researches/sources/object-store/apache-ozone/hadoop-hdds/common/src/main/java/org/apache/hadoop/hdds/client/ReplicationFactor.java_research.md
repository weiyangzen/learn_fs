## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationFactor.java

Purpose: client-facing replication factor enum for ONE and THREE.

Important APIs: `valueOf(int)`, `fromProto`, static and instance `toProto`, and `getValue`.

Control flow: only 1 and 3 are accepted from integers; null proto/client values round trip as null in static conversions; unknown proto values throw. State/persistence: enum constants only. Dependencies: HDDS protobufs.

Integration points: CLI/client parsing, replication config factories, default replication serialization. Risks: adding a new factor requires updates across switch statements and validation patterns; client enum names must remain aligned with protobuf enum names for some factory paths. Test signals: int conversion, null conversion, unsupported proto/int rejection, and proto round trip.
