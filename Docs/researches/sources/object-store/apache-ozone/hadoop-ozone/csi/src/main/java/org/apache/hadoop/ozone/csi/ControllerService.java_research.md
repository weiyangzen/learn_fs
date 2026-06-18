<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/java/org/apache/hadoop/ozone/csi/ControllerService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/java/org/apache/hadoop/ozone/csi/ControllerService.java

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/java/org/apache/hadoop/ozone/csi/ControllerService.java_research.md`.

## Purpose
CSI Controller gRPC implementation that maps Kubernetes volume create/delete calls to Ozone S3 bucket create/delete operations and advertises create/delete capability. The file has 116 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Types/classes: `ControllerService`. Methods and hooks: `ControllerService, createVolume, findSize, deleteVolume, controllerGetCapabilities`. Test annotations present: `0`.

## Control Flow
CreateVolume creates an Ozone S3 bucket, resolves capacity from required/limit/default bytes, emits `CreateVolumeResponse`, and translates `IOException` to gRPC error; DeleteVolume deletes the named S3 bucket; capability RPC returns only `CREATE_DELETE_VOLUME`.

## State And Persistence Behavior
Persistent external state is Ozone/S3 bucket creation/deletion and host mount table changes; in-memory state is limited to configuration fields, Ozone client handles, and gRPC server lifecycle.

## Dependencies And Integration Points
imports `csi.v1.ControllerGrpc.ControllerImplBase`, `csi.v1.Csi.CapacityRange`, `csi.v1.Csi.ControllerGetCapabilitiesRequest`, `csi.v1.Csi.ControllerGetCapabilitiesResponse`, `csi.v1.Csi.ControllerServiceCapability`, `csi.v1.Csi.ControllerServiceCapability.RPC`, `csi.v1.Csi.ControllerServiceCapability.RPC.Type`, `csi.v1.Csi.CreateVolumeRequest`.

## Risks And Edge Cases
- CSI idempotency and already-existing/missing bucket behavior depends on Ozone client exceptions.
- Capacity range handling ignores `limit_bytes` when `required_bytes` is set.

## Test Signals
No direct test harness is declared in this file; validation is indirect through consumers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/java/org/apache/hadoop/ozone/csi/ControllerService.java -->
