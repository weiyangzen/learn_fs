<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/DiskBalancerProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/DiskBalancerProtocol.proto

## Purpose

Defines the datanode disk-balancer control protocol: read current disk-balancer info, start balancing with a target plan, stop a running balancer, and update disk-balancer configuration.

## Important APIs, types, and functions

Package: `hadoop.hdds`. Imports: `hdds.proto`. Important declarations include `GetDiskBalancerInfoRequestProto, GetDiskBalancerInfoResponseProto, StartDiskBalancerRequestProto, StartDiskBalancerResponseProto, StopDiskBalancerRequestProto, StopDiskBalancerResponseProto, UpdateDiskBalancerConfigurationRequestProto, UpdateDiskBalancerConfigurationResponseProto, DiskBalancerProtocolService`. RPC methods: getDiskBalancerInfo(GetDiskBalancerInfoRequestProto -> GetDiskBalancerInfoResponseProto), startDiskBalancer(StartDiskBalancerRequestProto -> StartDiskBalancerResponseProto), stopDiskBalancer(StopDiskBalancerRequestProto -> StopDiskBalancerResponseProto), updateDiskBalancerConfiguration(UpdateDiskBalancerConfigurationRequestProto -> UpdateDiskBalancerConfigurationResponseProto).

## Control flow

The service has four unary RPCs. Requests carry a datanode identifier, balancing plan or configuration, and responses return status booleans/messages or DatanodeDiskBalancerInfoProto from hdds.proto.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Operational risk is around stale datanode UUIDs, malformed plans, concurrent start/stop calls, and config updates while a balancer is running. Tests should pin idempotency and validation behavior.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/DiskBalancerProtocol.proto -->
