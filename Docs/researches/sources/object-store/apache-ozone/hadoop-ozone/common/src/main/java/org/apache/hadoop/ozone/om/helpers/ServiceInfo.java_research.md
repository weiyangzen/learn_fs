<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ServiceInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ServiceInfo.java

## Purpose

`ServiceInfo` describes an Ozone service endpoint discovered from OM: node type, hostname, service ports, OM protocol version, optional OM role, and optional filesystem server defaults.

## Important APIs, Types, And Functions

Important methods are getters, `getPort`, `getServiceAddress`, `getOmRoleInfo`, `getServerDefaults`, `getProtobuf`, `getFromProtobuf`, and the nested `Builder` with node, host, port, OM version, role, and defaults setters.

## Control Flow, State, And Persistence

Instances are service-discovery DTOs. Construction copies protobuf `ServicePort` entries into a map. `getProtobuf` converts the map back to port messages and conditionally writes OM version, OM role, and server defaults. This information is returned by OM, not persisted by this class.

## Dependencies And Integration Points

It depends on HDDS `NodeType`, Ozone manager version, `OzoneFsServerDefaults`, and service-info protobuf types. It integrates with `OzoneManagerProtocol.getServiceList`, client discovery, OM HA role display, HTTP/RPC endpoint lookup, and OzoneFS defaults.

## Risks And Test Signals

`getPort` unboxes a nullable map value and throws if the port type is absent. Builder validation relies on constructor null checks for node and host only. Tests should cover port map round trips, missing port handling, OM role inclusion only for OM nodes, server-default compatibility, and JSON deserialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ServiceInfo.java -->
