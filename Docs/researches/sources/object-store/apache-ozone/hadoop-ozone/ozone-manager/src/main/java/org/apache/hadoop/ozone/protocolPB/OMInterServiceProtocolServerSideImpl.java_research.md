## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OMInterServiceProtocolServerSideImpl.java

Purpose: protobuf server-side translator for OM inter-service RPCs, currently bootstrapping new OM nodes into the Ratis ring.

Important APIs and types: implements `OMInterServiceProtocolPB`; constructor receives `OzoneManager` and `OzoneManagerRatisServer`; method `bootstrap` handles `BootstrapOMRequest`.

Control flow: null request returns null. For valid requests, it checks current OM leader status, builds `OMNodeDetails` from node id, host, Ratis port, and listener flag, then delegates to `omRatisServer.addOMToRatisRing`. IO failures return a response with `success=false`, `RATIS_BOOTSTRAP_ERROR`, and a stringified error.

State and persistence: the adapter owns only references; durable membership changes are handled by Ratis/OM configuration logic.

Dependencies and integration: used by OM peer bootstrap flows and depends on Ratis leader checks plus protobuf request/response types.

Risks and test signals: like the admin adapter, null request returns null. No explicit admin authorization appears in this inter-service path, so endpoint security must be enforced by transport/service configuration. Tests should cover leader rejection, node detail mapping, successful add, IO failure error code, listener flag propagation, and null request behavior.
