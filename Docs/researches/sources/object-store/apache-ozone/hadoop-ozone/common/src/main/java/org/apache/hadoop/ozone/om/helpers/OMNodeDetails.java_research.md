# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OMNodeDetails.java

Purpose: OM-specific node descriptor extending generic `NodeDetails` with RPC port, decommission state, and Ratis listener status.

Important APIs/types/functions: Builder constructs from host/RPC/Ratis/HTTP/HTTPS/service/node data. `getOMDBCheckpointEndpointUrl` builds v1 or v2 DB checkpoint URLs with snapshot-data and flush query parameters. `getOMNodeDetailsFromConf` reads RPC, Ratis, HTTP, HTTPS, and listener config. `getProtobuf`/`getFromProtobuf` convert `OMNodeInfo`.

Control flow and state: Mutable flags mark decommissioned and Ratis listener state. Config loading returns null if the OM RPC address is missing, creates socket addresses with error wrapping, and determines listener status from configured listener node IDs.

State and persistence behavior: `OMNodeInfo` protobuf carries node state for admin/cluster APIs. DB checkpoint URL construction controls remote checkpoint download behavior but does not persist state.

Dependencies and integration points: Used by OM HA/admin code, checkpoint transfer, and decommission/listener workflows. Depends on `OzoneConfiguration`, `OmUtils`, `ConfUtils`, `URIBuilder`, and admin protobufs.

Risks: URL building passes address strings as hosts; address formatting must be compatible with `URIBuilder`. Missing config silently returns null. Protobuf conversion omits service ID/http/https, so round-tripped objects have reduced context.

Test signals: Config-derived node details for service/node suffixes, listener detection, v1/v2 checkpoint URL query parameters, decommission protobuf round trip, and malformed address handling.
