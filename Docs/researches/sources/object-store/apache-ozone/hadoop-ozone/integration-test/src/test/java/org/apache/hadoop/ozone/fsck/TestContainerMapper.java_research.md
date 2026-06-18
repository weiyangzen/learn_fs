# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/fsck/TestContainerMapper.java

## Purpose
`TestContainerMapper` validates that the fsck `ContainerMapper` can parse an OM database and derive a container-to-key/block mapping after keys have been written into a stopped MiniOzoneCluster. It specifically uses object-store buckets because Recon's mapping did not support FSO buckets for the referenced TODO.

## Important APIs, Types, and Functions
- `init()` configures OM DB directory, 100 MB SCM containers, zero datanode free-space minimum, and an elevated pipeline owner container count, then writes twenty 10 MB keys.
- `testContainerMapper()` creates `ContainerMapper`, calls `parseOmDB(conf)`, and asserts the returned map has three containers.
- `generateData(...)` creates a fixed byte array used for all keys.
- `shutdown()` closes the client and shuts down the cluster.

## Control Flow
The setup method starts a three-datanode cluster, creates a random volume and object-store bucket, writes twenty keys with standalone replication factor one, closes the output streams, and stops the cluster so the DB can be parsed offline. The test then parses the OM DB and validates the expected container count.

## State and Persistence Behavior
The test writes real OM key metadata and data blocks, then relies on the persisted OM RocksDB path configured by `OZONE_OM_DB_DIRS`. The parsed result is a nested `Map<Long, List<Map<Long, BlockIdDetails>>>`, keyed by container ID, containing block details for keys.

## Dependencies and Integration Points
Dependencies include `MiniOzoneCluster`, `OzoneClientFactory`, object-store bucket creation, SCM container sizing, datanode Ratis space configuration, `ContainerMapper`, and the `BlockIdDetails` model.

## Risks and Test Signals
Risks include assumptions about container closure and allocation count: twenty 10 MB keys into 100 MB containers are expected to occupy three containers because containers close before the threshold. The main signal is the exact parsed container map size after offline OM DB parsing.
