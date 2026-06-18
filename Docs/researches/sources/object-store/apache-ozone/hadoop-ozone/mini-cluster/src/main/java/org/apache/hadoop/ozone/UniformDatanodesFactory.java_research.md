# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/UniformDatanodesFactory.java

## Purpose

`UniformDatanodesFactory` is a `MiniOzoneCluster.DatanodeFactory` that produces per-datanode configurations with consistent layout, volume count, reserved space, version settings, and short timing defaults. It is used by mini-cluster tests that need datanodes with predictable topology and storage characteristics.

## Important APIs and Types

- `apply(OzoneConfiguration)` clones the base configuration and returns a datanode-specific configuration.
- `configureDatanodePorts(ConfigurationTarget)` assigns loopback hostnames and free ports for HTTP, client, IPC, Ratis IPC/admin/server/datastream, and replication server ports.
- `Builder` exposes `setNumDataVolumes`, `setReservedSpace`, `setLayoutVersion`, `setInitialVersion`, `setCurrentVersion`, and `build`.

## Control Flow

Each `apply` call increments `nodesCreated`, clones the input config, allocates ports, derives a `datanode-N` base directory from `OZONE_METADATA_DIRS`, creates metadata, data, and Ratis directories, writes volume path lists and optional per-volume reserved-space strings, optionally initializes `DatanodeLayoutStorage`, optionally writes test initial/current datanode versions, and shortens leader election and heartbeat intervals.

## State and Persistence

The factory's only in-memory mutable state is an `AtomicInteger` counter. It creates real directories on disk for metadata, data volumes, and Ratis storage. Optional layout initialization persists layout metadata before the datanode service starts.

## Dependencies and Integration Points

It depends on HDDS/Ozone config keys, `DatanodeLayoutStorage`, `DatanodeVersion`, `ReplicationServer.ReplicationConfig`, and `GenericTestUtils.PortAllocator`. It integrates with `MiniOzoneCluster` by returning a complete config for each datanode service.

## Risks and Edge Cases

`OZONE_METADATA_DIRS` must be present or `Objects.requireNonNull` fails. Reserved-space strings are set to an empty string when no reserved space is configured, which downstream parsers must tolerate. The factory assumes directories can be created and ports remain free until service bind. Layout/current/initial version combinations can create upgrade/downgrade test states, so callers must choose compatible versions.

## Test Signals

Useful tests assert unique per-node directories and ports, correct number of data volumes, correct reserved-space formatting, layout metadata creation, and propagation of initial/current test versions.
