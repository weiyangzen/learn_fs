<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/ReconfigureProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/ReconfigureProtocol.proto

## Purpose

Defines the generic runtime reconfiguration RPC contract used to identify a server, start reconfiguration, query reconfiguration status, and list reconfigurable properties.

## Important APIs, types, and functions

Package: `hadoop.hdds`. Imports: none. Important declarations include `GetServerNameRequestProto, GetServerNameResponseProto, StartReconfigureRequestProto, StartReconfigureResponseProto, GetReconfigureStatusRequestProto, GetConfigurationChangeProto, GetReconfigureStatusResponseProto, ListReconfigurePropertiesRequestProto, ListReconfigurePropertiesResponseProto, ReconfigureProtocolService`. RPC methods: getServerName(GetServerNameRequestProto -> GetServerNameResponseProto), getReconfigureStatus(GetReconfigureStatusRequestProto -> GetReconfigureStatusResponseProto), startReconfigure(StartReconfigureRequestProto -> StartReconfigureResponseProto), listReconfigureProperties(ListReconfigurePropertiesRequestProto -> ListReconfigurePropertiesResponseProto).

## Control flow

Clients call startReconfigure, then poll getReconfigureStatus. Status responses contain the start/end timestamps and repeated GetConfigurationChangeProto entries with property, old value, new value, and error text.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

The protocol exposes mutable runtime configuration, so authorization and server-side property validation are crucial. Empty strings and absent fields can be ambiguous for old/new values.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/ReconfigureProtocol.proto -->
