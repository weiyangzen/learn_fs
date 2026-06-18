<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/java/org/apache/hadoop/ozone/csi/NodeService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/java/org/apache/hadoop/ozone/csi/NodeService.java

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/java/org/apache/hadoop/ozone/csi/NodeService.java_research.md`.

## Purpose
CSI Node gRPC implementation that publishes Ozone S3 buckets by creating target directories and running a configured FUSE mount command, and unpublishes through `fusermount -u`. The file has 148 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Types/classes: `NodeService`. Methods and hooks: `NodeService, nodePublishVolume, executeCommand, nodeUnpublishVolume, nodeGetCapabilities, nodeGetInfo`. Test annotations present: `0`.

## Control Flow
Publish creates the target directory, formats the configured mount command with S3 endpoint, volume ID, and target path, runs it with a 10-second wait, and returns an empty response; unpublish formats and runs `fusermount -u`; node info resolves the local host name.

## State And Persistence Behavior
Persistent external state is Ozone/S3 bucket creation/deletion and host mount table changes; in-memory state is limited to configuration fields, Ozone client handles, and gRPC server lifecycle.

## Dependencies And Integration Points
imports `csi.v1.Csi.NodeGetCapabilitiesRequest`, `csi.v1.Csi.NodeGetCapabilitiesResponse`, `csi.v1.Csi.NodeGetInfoRequest`, `csi.v1.Csi.NodeGetInfoResponse`, `csi.v1.Csi.NodePublishVolumeRequest`, `csi.v1.Csi.NodePublishVolumeResponse`, `csi.v1.Csi.NodeUnpublishVolumeRequest`, `csi.v1.Csi.NodeUnpublishVolumeResponse`; tools `fusermount`.

## Risks And Edge Cases
- `Runtime.exec(command)` receives a formatted command string, so command template and volume/target values must stay trusted.
- The process wait result is not checked before `exitValue()`, so long-running mounts can fail with timing-sensitive behavior.
- Mount/unmount operations depend on host FUSE tooling and permissions.

## Test Signals
No direct test harness is declared in this file; validation is indirect through consumers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/csi/src/main/java/org/apache/hadoop/ozone/csi/NodeService.java -->
