<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/proto/csi.proto -->
# sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/proto/csi.proto

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/proto/csi.proto_research.md`.

## Purpose
Vendored Container Storage Interface v1 protobuf contract used to generate `csi.v1` gRPC Java APIs consumed by the Ozone CSI service. The file has 1323 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
The proto exports CSI `Identity`, `Controller`, and `Node` services plus request/response messages for volume, snapshot, topology, capacity, expansion, node stats, and capability negotiation. Visible services: Identity, Controller, Node; representative RPCs: GetPluginInfo, GetPluginCapabilities, Probe, CreateVolume, DeleteVolume, ControllerPublishVolume, ControllerUnpublishVolume, ValidateVolumeCapabilities, ListVolumes, GetCapacity, ControllerGetCapabilities, CreateSnapshot.

## Control Flow
The file is declarative: generated gRPC stubs route client calls to service implementations, and request/response messages carry CSI state such as volume IDs, secrets, topology, capacity ranges, and node paths.

## State And Persistence Behavior
No local persistence; generated classes serialize/deserialize CSI request state over gRPC and preserve backwards-compatible field numbers.

## Dependencies And Integration Points
imports `"google/protobuf/descriptor.proto"`, `"google/protobuf/timestamp.proto"`, `"google/protobuf/wrappers.proto"`; CSI services `Identity`, `Controller`, `Node`.

## Risks And Edge Cases
- CSI field numbers and message names are API compatibility surface; incompatible edits break generated clients/servers.
- Secret fields are annotated but downstream logging/handling must still avoid disclosure.

## Test Signals
Signal comes from protobuf/gRPC code generation and compile-time compatibility of generated CSI service/message classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/proto/csi.proto -->
