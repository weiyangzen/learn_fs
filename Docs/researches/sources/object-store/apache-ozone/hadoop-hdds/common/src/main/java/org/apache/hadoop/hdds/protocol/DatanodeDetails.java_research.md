## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/protocol/DatanodeDetails.java

Purpose: central datanode identity and endpoint descriptor, extending SCM network topology `NodeImpl` and providing protobuf/DB codec support.

Important APIs: `getCodec`, ID/UUID accessors, IP/host setters/getters, `validateDatanodeIpAddress`, synchronized port setters/getters, operational state helpers for decommission/maintenance, proto builders/parsers, extended proto conversion, version/setup/revision fields, compare/equality, builder, and nested `Port` value type with port name sets.

Control flow: builder parsing supports current `id` plus older `uuid128`/string UUID fields. Proto serialization writes current and deprecated UUID fields, byte-string host/IP fields, network topology, persisted operational state, expiry, and ports. Port serialization filters by requested port set and by client version: old clients receive only V0 ports, while newer clients can handle unknown ports. `getPort` falls back from RATIS_ADMIN, RATIS_SERVER, and RATIS_DATASTREAM to the legacy RATIS port for compatibility; `hasPort(Name)` checks explicit presence without fallback. `validateDatanodeIpAddress` resolves hostname and updates changed IPs.

State/persistence: mutable datanode metadata, volatile persisted op-state fields, synchronized port list access, DB codec via delegated proto codec. Equality and hash are based only on immutable `DatanodeID`.

Dependencies: HDDS protobufs, layout-feature annotations, client version gates, `DatanodeID`, `StringWithByteString`, network topology classes, DB codecs, DNS resolution, and logging.

Integration points: SCM node manager, datanode registration/heartbeat, pipelines, Ratis peer construction, network topology, persisted metadata, upgrade compatibility, and client-facing protobuf APIs. Risks: mutable fields on an equality-by-ID object can obscure stale endpoint data; port fallback can hide missing split Ratis ports; client-version filtering must track new port names; ignored unknown port names in proto parsing can lose endpoints; IP validation performs DNS lookups and logs but does not fail hard. Test signals: proto compatibility across client versions, unknown/filtered ports, legacy UUID fields, operational state defaults/expiry, builder defaults for network location, copy constructor, DB codec round trip, and explicit-vs-fallback port behavior.
