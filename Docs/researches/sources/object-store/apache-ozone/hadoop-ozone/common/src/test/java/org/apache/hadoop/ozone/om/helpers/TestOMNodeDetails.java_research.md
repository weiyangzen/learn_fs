# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOMNodeDetails.java

Purpose: tests `OMNodeDetails`, the metadata holder for OM node identity, addresses, ports, listener/decommission state, protobuf conversion, and checkpoint endpoint URL generation.

Important APIs/types/functions: exercises builder setters for service ID, node ID, host/RPC/Ratis/HTTP/HTTPS addresses, `setIsListener`, `setRatisAddress`, getters, `setRatisListener`, `setDecommissioningState`, `getProtobuf`, `getFromProtobuf`, `getOMPrintInfo`, `getOMDBCheckpointEndpointUrl`, `getOMNodeAddressFromConf`, and `getOMNodeDetailsFromConf`.

Control flow and state: tests construct nodes from `InetSocketAddress` and host strings, mutate listener/decommission flags, round-trip active/decommissioned/listener nodes through `OMNodeInfo`, and read node address fields from `OzoneConfiguration`.

Dependencies and integration points: integrates with OM config keys, `ConfUtils`, admin protobuf `OMNodeInfo` and `NodeState`, and checkpoint HTTP/HTTPS endpoint construction.

Risks and test signals: catches wrong host/port derivation, missing listener state in protobuf, decommission state loss, malformed checkpoint URLs, and null handling for incomplete config. Checkpoint URL tests verify protocol, authority, path version, and query flags like `flushBeforeCheckpoint` and `includeSnapshotData`.
