# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestContainerReportWithKeys.java

## Purpose

`TestContainerReportWithKeys` verifies that after key writes, SCM receives container reports and tracks container replica/key-related metadata consistently enough to locate the written containers and replicas.

## Important APIs, Types, And Functions

The abstract non-HA test uses `OzoneClient`, `ObjectStore`, `OzoneOutputStream`, `StorageContainerManager`, `OmKeyArgs`, `OmKeyLocationInfo`, `ContainerInfo`, and `ContainerReplica`. It writes random data through the object-store API and inspects SCM container state.

## Control Flow

Setup captures the cluster client and SCM. The test creates volume/bucket/key data, closes the output stream, resolves key location information through OM helpers, and checks the corresponding SCM container and replica information after reports arrive.

## State And Persistence Behavior

The test writes durable key data to datanodes and persists OM key metadata. SCM state is updated asynchronously by datanode container reports carrying container/replica information.

## Dependencies And Integration Points

It links Ozone object-store writes, OM key-location metadata, SCM container manager, replica tracking, and datanode container reports.

## Risks And Test Signals

The major risk is report timing. Failures indicate missing container reports after writes, stale SCM replica maps, or divergence between OM key locations and SCM container metadata.
